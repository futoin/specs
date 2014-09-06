<pre>
FTN6: FutoIn Async API
Version: 1.0
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# 1. Concept

This interface was born as a secondary option for
executor concept. However, it quickly became clear that
async/reactor/proactor/light threads/etc. should be base
for scalable high performance server implementations, even though it is more difficult for understanding and/or debugging.
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
to make cleanup actions and complete job with error.

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

AsyncSteps must support derived classes in implementation-defined way.
Typical use case: functionality extension (e.g. request processing API).

## 1.1. Levels

When AsyncSteps (or derived) object is created all steps are added
sequentially in Level 0 through add() and/or parallel(). Note: each
parallel() is seen as a step.

After AsyncSteps execution is initiated, each step of Level 0 is executed.
All sub-steps are added in Level n+1. Example:

    add() -> Level 0 #1
        add() -> Level 1 #1
            add() -> Level 2 #1
            parallel() -> Level 2 #2
            add() -> Level 2 #3
        parallel() -> Level 1 #2
        add() -> Level 1 #3
    parallel() -> Level 0 #2
    add() -> Level 0 #3

    
Execution cannot continue to the next step of current Level until all steps of higher Level
are executed.

The execution sequence would be:

    Level 0 add #1
    Level 1 add #1
    Level 2 add #1
    Level 2 parallel #2
    Level 2 add #3
    Level 1 parallel #2
    Level 1 add #3
    Level 0 parallel #2
    Level 0 add #3

## 1.2. Error handling

Due to not linear programming, classic try/catch blocks are converted into execute/onerror.
Each added step may have custom error handler. If error handler is not specified then
control passed to lower Level error handler. If non is defined then execution is aborted.

Example:

    add( -> Level 0
        func( as ){
            print( "Level 0 func" )
            add( -> Level 1
                func( as ){
                    print( "Level 1 func" )
                    as.error( "myerror" )
                },
                onerror( as, error ){
                    print( "Level 1 onerror: " + error )
                    as.error( "newerror" )
                }
            )
        },
        onerror( as, error ){
            print( "Level 0 onerror: " + error )
            as.success( "Prm" )
        }
    )
    add( -> Level 0
        func( as, param ){
            print( "Level 0 func2: " + param )
            as.success()
        }
    )


Output would be:

    Level 0 func
    Level 1 func
    Level 1 onerror: myerror
    Level 0 onerror: newerror
    Level 0 func2: Prm
    
In synchronous way, it would look like:

    variable = null

    try
    {
        print( "Level 0 func" )
        
        try
        {
            print( "Level 1 func" )
            throw "myerror"
        }
        catch ( error )
        {
            print( "Level 1 onerror: " + error )
            throw "newerror"
        }
    }
    catch( error )
    {
        print( "Level 0 onerror: " + error )
        variable = "Prm"
    }
    
    print( "Level 0 func2: " + variable )


## 1.3. Wait for external resources

Very often, execution of step cannot continue without waiting for external event like input from network or disk.
It is forbidden to block execution in event waiting. As a solution, there are special setTimeout() and setCancel()
methods.

Example:

    add(
        func( as ){
            socket.read( function( data ){
                as.success( data )
            } )
            
            as.setCancel( function(){
                socket.cancel_read()
            } )
            
            as.setTimeout( 30_000 ) // 30 seconds
        },
        onerror( as, error ){
            if ( error == timeout ) {
                print( "Timeout" )
            }
            else
            {
                print( "Read Error" )
            }
        }
    )

## 1.4. Parallel execution abort

Definition of parallel steps makes no sense to continue execution if any of steps fails. To avoid
excessive time and resources spent on other steps, there is a concept of canceling execution similar to 
timeout above.

Example:
    
    as.parallel()
        .add(
            func( as ){
                as.setCancel( function(){ ... } )
                
                // do parallel job #1
                as.state()->result1 = ...;
            }
        )
        .add(
            func( as ){
                as.setCancel( function(){ ... } )

                // do parallel job #1
                as.state()->result2 = ...;
            }
        )
        .add(
            func( as ){
                as.error( "Some Error" )
            }
        )
    as.add(
        func( as ){
            print( as.state()->result1 + as.state->result2 )
            as.success()
        }
    )



# 2. Async Steps API

## 2.1. Types

* *void execute_callback( AsyncSteps as[, previous_success_args] )*
    * first argument is always AsyncSteps object
    * other arguments come from previous as.success() call, if any
    * returns nothing
    * behavior:
        * either set completion status through as.success() or as.error()
        * or add sub-steps through as.add() and/or as.parallel()
        * any violation is reported as as.error( InternalError )
    * can use as.state() for global current job state data
    * can limit time for sub-step processing with setTimeout()
* *void error_callback( AsyncSteps as, error )*
    * the first argument is always AsyncSteps object
    * the second argument comes previous as.error() call
    * returns nothing
    * behavior, completes through:
        * as.success() - continue execution from the next step, after return
        * as.error() - change error string
        * return - continue unwinding error handler stack
        * any violation is reported as as.error( InternalError )
    * can use as.state() for global current job state data
* *void cancel_callback( AsyncSteps as )*
    * it must be used to cancel out of AsyncSteps program flow actions, like
        waiting on connection, timer, dedicated task, etc.

    
## 2.2. Functions

1. *AsyncSteps add( execute_callback func[, error_callback onerror] )*
    - add step, getting async interface as parameter
    * can be called multiple times to add sub-steps of the same level (sequential execution)
    * steps are queued in the same execution level (sub-steps create a new level)
    * returns current level AsyncSteps object accessor
2. *AsyncSteps parallel( [error_callback onerror] )*
    * creates a step and returns specialization of AsyncSteps interface
        * all add()'ed sub-steps are executed in parallel (not strictly required)
        * the next step in current is executed only when all parallel steps complete
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
9. *get/set/exists/unset* wildcard accessor, which map to state() variables
    * only if supported by language/platform
10. *execute()* - must be called only once after Level 0 steps are configured.
    * Initiates AsyncSteps execution implementation-defined way
    
    
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