<pre>
FTN6: FutoIn Async API
Version: 0.9
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# 1. Concept

This interface was born as a secondary option for
executor concept. However, it quickly became clear that
async/reactor/proactor/light threads/etc. is base
for scalable high performance server implementations.
Traditional synchronous program flow becomes an addon
on top of asynchronous base for legacy code and/or too
complex logic.

Program flow is split into non-blocking execution steps, represented
with execution callback function. Processing Unit (eg. CPU) halting/
spinning/switching-to-another-task is seen as a blocking action in program flow.

Any step must not call any of blocking functions, except for synchronization
with guaranteed minimal period of lock acquisition.
*Note: under minimal period, it is assumed that any acquired lock is 
immediately released after action with O(1) complexity and no delay
caused by programmatic suspension/locking of executing task*

Every step is executed sequentially. Success result of any step
becomes input for the following step.

Each step can have own error handler. Error handler is called, if
AsyncSteps.error() is called within step execution or any of its 
sub-steps. Typical behavior is to ignore error and continue or
to make cleanup actions and complete request with error.

Each step can have own sequence of sub-steps. Sub-steps can be added
only during that step execution. Sub-step sequence is executed after
current step execution is finished.

If there are any sub-steps added then current step must not call
AsyncSteps.success() or AsyncSteps.error(). Otherwise, InternalError
is raised.

It is possible to create a special "parallel" sub-step and add
independent sub-steps to it. Execution of each parallel sub-step
is started all together. Parallel step completes with success
when all sub-steps complete with success. If error is raised in
any sub-step of parallel step then all other sub-steps are canceled.

Out-of-order cancel of execution can occur by timeout, 
execution control engine decision (e.g. Invoker disconnect) or
failure of sibling parallel step. Each step can install custom
on-cancel handler to free resources and/or cancel external jobs.
After cancel, it must be safe to destroy AsyncSteps object.

AsyncSteps must be used in Executor request processing. The same 
[root] AsyncSteps object must be used for all asynchronous tasks within
given request processing.

AsyncSteps may be used by Invoker implementation.


# 2. Async Steps API

## 2.1. Types

* *void execute_callback( AsyncSteps as[, previous_success_args] )*
    * first argument is always AsyncSteps object
    * other arguments come from previous as.success() call, if any
    * returns nothing
    * behavior:
        * either complete through as.success() or as.error()
        * or add sub-steps through as.add() and/or as.parallel()
        * any violation is reported as as.error( InternalError )
    * can use as.state() for global current request state data
    * can limit time for sub-step processing with setTimeout()
* *void error_callback( AsyncSteps as, error )*
    * the first argument is always AsyncSteps object
    * the second argument comes previous as.error() call
    * returns nothing
    * behavior, completes through:
        * as.success() - continue execution from the next step
        * as.error() - change error string
        * return
        * any violation is reported as as.error( InternalError )
    * can use as.state() for global current request state data
* *void cancel_callback( AsyncSteps as )*
    it * must be used to cancel out of AsyncSteps program flow actions, like
        waiting on connection, timer, dedicated task, etc.

    
## 2.2. Functions

1. *AsyncSteps add( execute_callback func[, error_callback onerror] )*
    - add step, getting async interface as parameter
    * can be called multiple times to add sub-steps of the same level
    * insert position starts right after the current called step
    * returns current AsyncSteps object reference
2. *AsyncSteps parallel( [error_callback onerror] )*
    * creates a step and returns specialization of AsyncSteps interface
        * all add()'ed sub-steps are executed in parallel
        * next step is executed only when all steps complete
        * sub-steps of parallel steps follow normal sequential semantics
        * success() does not allow any arguments - use state() to pass results
3. *void success( [result_arg, ...] )*
    * successfully complete current step execution. Should be called from func()
4. *void error( name )*
    * complete with error
    * does NOT throw exception/abort execution
    * calls onerror( async_iface, name )
4. *Map state()*
    * returns reference to map, which can be populated with arbitrary state values
6. *void setTimeout( timeout_ms )*
    * inform execution engine to wait for either success() or error()
    for specified timeout in ms. On timeout, error("Timeout") is called
7. *call operator overloading*
    * if supported by language/platform, alias for success()
8. *void setCancel( cancel_callback oncancel )*
    * set callback, to be used to cancel execution
9. get/set/exists/unset wildcard accessor functions, which map to state() variables
    * only if supported by language/platform
    
    
# 3. Example

In pseudo-code.

## 3.1. Single-level steps

    AsyncStepsImpl as;

    as.add(
        function( inner_as ){
            if ( something )
                inner_as.success( 1, 2 )
            else
                inner_as.error( NotImplemented )
        },
        function( inner_as, error ){
            externalError( error );
        }
    ).add(
        function( inner_as, res1, res2 ){
            externalSuccess( res1, res2 );
            inner_as.success()
        },
    )

## 3.2. Sub-steps

    AsyncStepsImpl as;

    as.add(
        function( inner_as ){
            inner_as.add(
                function( inner2_as ){
                    if ( something )
                        inner2_as.success( 1 )
                    else
                        inner2_as.error( NotImplemented )
                },
                function( inner2_as, error )
                {
                    log( "Spotted error " + error )
                    // continue with higher level error handlers
                }
            )
            inner_as.add(
                function( inner2_as, res1 ){
                    inner2_as.success( res1, 2 )
                }
            )
        },
        function( inner_as, error ){
            externalError( error );
        }
    ).add(
        function( inner_as, res1, res2 ){
            externalSuccess( res1, res2 );
            inner_as.success()
        },
    )
    
## 3.3. parallel() steps and state()

    AsyncStepsImpl as;

    as.add(
        function( inner_as ){
            inner_as.parallel().add(
                function( inner2_as ){
                    inner2_as.state().parallel_1 = 1;
                    inner2_as.success()
                },
                function( inner2_as, error )
                {
                    log( "Spotted error " + error )
                    // continue with higher level error handlers
                }
            ).add(
                function( inner2_as ){
                    inner2_as.state().parallel_2 = 2;
                    inner2_as.success()
                },
                function( inner2_as, error )
                {
                    inner2_as.state().parallel_2 = 0;
                    inner2_as.success()
                    // ignore error
                }
            )
        },
        function( inner_as, error ){
            externalError( error );
        }
    ).add(
        function( inner_as, res1, res2 ){
            externalSuccess(
                as.state().parallel_1,
                as.state().parallel_2
            );
            inner_as.success()
        },
    )
