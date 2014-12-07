<pre>
FTN12: FutoIn Async API
Version: 1.4DV
Date: 2014-12-01
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.4 - 2014-12-01
    * Updated 1.6.1 and renamed to "The Safety Rules of AsyncSteps helpers"
    * Added .util() specification
* v1.3 - 2014-10-18
    * Documented existing any way as.cancel()
    * Split AsyncSteps API in logical groups for better understanding
* v1.2 - 2014-09-30
    * Added concept of successStep()
    * Added "error_info" convention
    * Changed behavior of as.error() to throw exception (not backward-compatible, but more like a bugfix)
* v1.1 - 2014-09-07
    * Added cloning concept and requirements
* v1.0 - 2014-08-31

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

For performance reasons, it is not economical to initialize AsyncSteps
with business logic every time. Every implementation must support
platform-specific AsyncSteps cloning/duplicating.

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

## 1.5. AsyncSteps cloning

In long living applications the same business logic may be re-used multiple times
during execution.

In a REST API server example, complex business logic can be defined only once and
stored in a kind of AsyncSteps object repository.
On each request, a reference object from the repository would be copied for actual
processing with minimal overhead.

However, there would be no performance difference in sub-step definition unless
its callback function is also created at initialization time, but not at parent
step execution time (the default concept). So, it should be possible to predefine
those as well and copy/inherit during step execution. Copying steps must also
involve copying of state variables.

Example:

    AsyncSteps req_repo_common;
    req_repo_common.add(func( as ){
        as.add( func( as ){ ... } );
        as.copyFrom( as.state().business_logic );
        as.add( func( as ){ ... } );
    });
    
    AsyncSteps req_repo_buslog1;
    req_repo_buslog1
        .add(func( as ){ ... })
        .add(func( as ){ ... });

    AsyncSteps actual_exec = copy req_repo_common;
    actual_exec.state().business_logic = req_repo_buslog1;
    actual_exec.execute();

However, this approach only make sense for deep performance optimizations.

## 1.6. "Success Step" and Throw

During development, when step flow is not known at coding time, but dynamically resolved
based on configuration, internal state, etc., it is common to see the following logic:

    as.add(func( as ){
        someHelperA( as ); // adds sub-step
        someHelperB( as ); // does nothing
        
        // Not effective
        as.add(func( as ){
            as->success();
        })
    })
    
The idea is that is it not known in advance if someHelper*() adds sub-steps or not. However, we must ensure
that a) only one success() call is yield b) there are no sub-steps. 

To make this elegant and efficient, a "success step" concept can be introduced:

    as.add(func( as ){
        someHelperA( as ); // adds sub-step
        someHelperB( as ); // does nothing
        
        // Runtime optimized
        as.successStep();
    })
    
As a counterpart for error handling, we must ensure that execution has stopped after error
is triggered in someHelper*() with no enclosing sub-step. The only safe way is to throw exception
what is now done in as.error()

### 1.6.1. The Safety Rules of AsyncSteps helpers

1. as.success() should be called only in top-most function of the
    step (the one passed to as.add() directly)
1. if top-most functions calls abstract helpers then it should call as.successStep()
    for safe and efficient successful termination
1. setCancel() and/or setTimeout() must be called only in top most function


## 1.7. Error Info

Error code is not always descriptive enough, especially, if it can be generated in multiple ways.
As a convention special "error_info" state field should hold descriptive information of the last error.

For convenience, error() is extended with optional parameter error_info


# 2. Async Steps API

## 2.1. Types

* *void execute_callback( AsyncSteps as[, previous_success_args] )*
    * first argument is always AsyncSteps object
    * other arguments come from the previous as.success() call, if any
    * returns nothing
    * behavior:
        * either set completion status through as.success() or as.error()
        * or add sub-steps through as.add() and/or as.parallel()
        * any violation is reported as as.error( InternalError )
    * can use as.state() for global current job state data
    * can limit time for sub-step processing with setTimeout()
* *void error_callback( AsyncSteps as, error )*
    * the first argument is always AsyncSteps object
    * the second argument comes from the previous as.error() call
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

It is assumed that all functions in this section are part of **single AsyncSteps interface**.
However, they are grouped by semantical scope of use.

### 2.2.1. Common API - can be used in any context

1. *AsyncSteps add( execute_callback func[, error_callback onerror] )*
    * add step, executor callback gets async interface as parameter
    * can be called multiple times to add sub-steps of the same level (sequential execution)
    * steps are queued in the same execution level (sub-steps create a new level)
    * returns current level AsyncSteps object accessor
1. *AsyncSteps parallel( [error_callback onerror] )*
    * creates a step and returns specialization of AsyncSteps interface
        * all add()'ed sub-steps are executed in parallel (not strictly required)
        * the next step in current level is executed only when all parallel steps complete
        * sub-steps of parallel steps follow normal sequential semantics
        * success() does not allow any arguments - use state() to pass results
1. *Map state()*
    * returns reference to map/object, which can be populated with arbitrary state values
1. *get/set/exists/unset* wildcard accessor, which map to state() variables
    * only if supported by language/platform
1. *AsyncSteps copyFrom( AsyncSteps other )*
    * Copy steps and state variables not present in current state
    from other(model) AsyncSteps object
    * See cloning concept
1. *clone*/*copy c-tor* - implementation-defined way of cloning AsyncSteps object

### 2.2.2. Execution API - can be used only inside execute_callback

*Note: success() and error() can be used in error_callback as well*

1. *void success( [result_arg, ...] )*
    * successfully complete current step execution. Should be called from func()
1. *void successStep()*
    * efficiently add as.success() call or a sub-step with as.success()
        call, if there are other sub-steps added
    * run-time should optimize the sub-step case
1. *void error( name [, error_info] )*
    * complete with error
    * throws FutoIn.Error exception
    * calls onerror( async_iface, name ) after returning to execution engine
    * *error_info* - assigned to "error_info" state field
1. *void setTimeout( timeout_ms )*
    * inform execution engine to wait for either success() or error()
    for specified timeout in ms. On timeout, error("Timeout") is called
1. *call operator overloading*
    * if supported by language/platform, alias for success()
1. *void setCancel( cancel_callback oncancel )*
    * set callback, to be used to cancel execution
1. *Utils utils()*
    * Returns advanced utility interface

### 2.2.3. Control API - can be used only on Root AsyncSteps object

1. *execute()* - must be called only once after root object steps are configured.
    * Initiates AsyncSteps execution implementation-defined way
1. *cancel()* - may be called on root object to asynchronously cancel execution

### 2.2.4. Utils API - advanced, but not essential tools
1. *void while( cond, func, [, label] )*
    * while *cond( as )* execute *func( as )*  returns true
    * *func* - loop body
    * *cond* - condition to check before each execution
    * *label* - optional label to use for *break()* and *continue()* in inner loops
1. *void forEach( map|list, func [, label] )*
    * for each *map* or *list* element call *func( as, key, value )*
    * *label* - optional label to use for *break()* and *continue()* in inner loops
1. *void repeat( count, func [, label] )*
    * Call *func(as, i)* for *count* times
    * *count* - how many times to call the *func*
    * *func( as, i )* - loop body, i - current iteration starting from 0
    * *label* - optional label to use for *break()* and *continue()* in inner loops
1. *void break( [label] )*
    * break execution of current loop
    * *label* - unwind loops, until *label* named loop is exited
1. *void continue( [label] )*
    * continue loop execution from the next iteration
    * *label* - break loops, until *label* named loop is found

    
# 3. Examples

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
    
=END OF SPEC=
