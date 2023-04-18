<pre>
FTN12: FutoIn Async API
Version: 1.14DV
Date: 2023-03-29
Copyright: 2014-2023 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.14 - 2023-03-29 - Andrey Galkin
    * FIXED: minor wording and grammar fixes
    * NEW: universal binary interface
    * NEW: formal documentation of AsyncTool interface
* v1.13.1 - 2018-09-24 - Andrey Galkin
    * FIXED: cosmetic markup issues
* v1.13 - 2018-09-18 - Andrey Galkin
    * NEW: newInstance() API
    * NEW: boolean cast checks
    * NEW: stack() API
* v1.12 - 2018-06-08 - Andrey Galkin
    * NEW: promise() wrapper for execute()
* v1.11 - 2018-02-02 - Andrey Galkin
    * CHANGED: successStep() to be used for result injection
    * CHANGED: cosmetic fixes for API definition
    * NEW: Promise/await integration
* v1.10 - 2017-12-06 - Andrey Galkin
    * NEW: added max queue length for `Mutex` and `Throttle`
    * NEW: `Limiter` primitive
* v1.9 - 2017-11-17 - Andrey Galkin
    * NEW: async_stack state variable
    * NEW: adding steps in error handler
* v1.8 - 2017-08-29 - Andrey Galkin
    * Added .sync() API & protocol
    * Added .waitExternal()
    * Added Mutex class
    * Added Throttle class
* v1.7 - 2015-06-01
    * Removed .utils() artifact
    * Added 1.10 "Reserved keyword name clash"
* v1.6 - 2015-01-02
    * Added last_exception state variable
* v1.5 - 2014-12-09
    * Added concept of implicit as.success()
    * Deprecated as.successStep()
    * Updated examples
    * Updated "The Safety Rules of libraries with AsyncSteps interface"
* v1.4 - 2014-12-09
    * Updated 1.6.1 and renamed to "The Safety Rules of AsyncSteps helpers"
    * Added 1.8 "Async Loops" and extended interface
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
async/reactor/proactor/light threads/etc. should be the base
of scalable high performance server implementations, even though it is
more difficult for understanding and/or debugging.
Traditional synchronous program flow becomes an addon
on top of asynchronous base for legacy code and/or too
complex logic. Academical and practical research in this direction
was started in field of cooperative multitasking back in XX century.

Program flow is split into non-blocking execution steps, represented
with execution callback function. Processing Unit (eg. CPU) halting/
spinning/switching-to-another-task is seen as a blocking action in program flow.
Execution of such fragments is partially ordered.

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

Due to non-linear programming, classic try/catch blocks are converted into execute/onerror.
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

## 1.2.1. Steps in error handler

Very often, error handler creates an alternative complex program path which
requires own async operation. Therefore, error handler must accept `as.add()`
as implicit `as.success()`.

If steps are added inside error handler they must remain on the same async stack
level while error handler itself gets removed.

Example:

    add( -> Level 0
        func( as ){
            print( "Level 0 func" )
            add( -> Level 1
                func( as ){
                    print( "Level 1 func" )
                    as.error( "first" )
                },
                onerror( as, error ){
                    print( "Level 1 onerror: " + error )
                    as.add( -> Level 2
                        func() {
                            print( "Level 2 func" )
                            as.error( "second" );
                        },
                        onerror( as, error ) {
                            print( "Level 2 onerror: " + error )
                        }
                    )
                }
            )
        },
        onerror( as, error ){
            print( "Level 0 onerror: " + error )
        }
    )


Output would be:

    Level 0 func
    Level 1 func
    Level 1 onerror: first
    Level 2 func
    Level 2 onerror: second
    Level 0 onerror: second

*Note: "Level 1 onerror" is not executed second time!*

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

However, this approach only makes sense for deep performance optimizations.

## 1.6. Implicit as.success()

If there are no sub-steps added, no timeout set and no cancel handler set then
implicit `as.success()` call is assumed to simplify code and increase efficiency.

    as.add(func( as ){
        doSomeStuff( as );
    })

As in many cases it's required to wait for external event without any additional
conditions, the general approach used to be adding an empty cancel handler. To
avoid that, an explicit `as.waitExternal()` API is available.

## 1.7. Error Info, Last Exception and Async Call Stack

Pre-defined state variables:

* **error_info** - value of the second parameter passed to the last *as.error()* call
* **last_exception** - the last exception caught, if feasible
* **async_stack** - implementation-defined stack of step handler references

Error code is not always descriptive enough, especially, if it can be generated in multiple ways.
As a convention, special `error_info` state field should hold descriptive information of the last error.
Therefore, `as.error()` is extended with optional parameter `error_info`.

The `last_exception` state variables may hold the last exception object caught, if feasible
to implement. It should be populated with FutoIn errors as well.


## 1.8. Async Loops

Almost always, async program flow is not linear. Sometimes, loops are required.

Basic principals of async loops:

        as.loop( func( as ){
            call_some_library( as );
            as.add( func( as, result ){
                if ( !result )
                {
                    // exit loop
                    as.break();
                }
            } );
        } )
        
Inner loops and identifiers:

        // start loop
        as.loop( 
            func( as ){
                as.loop( func( as ){
                    call_some_library( as );
                    as.add( func( as, result ){
                        if ( !result )
                        {
                            // exit loop
                            as.continue( "OUTER" );
                        }

                        as.success( result );
                    } );
                } );
                
                as.add( func( as, result ){
                    // use it somehow
                    as.success();
                } );
            },
            "OUTER"
        )
        
Loop n times.

        as.repeat( 3, func( as, i ){
            print( 'Iteration: ' + i )
        } )
        
Traverse through list or map:

        as.forEach(
            [ 'apple', 'banana' ],
            func( as, k, v ){
                print( k + " = " + v )
            }
        )
        
### 1.8.1. Termination

Normal loop termination is performed either by loop condition (e.g. `as.forEach()`, `as.repeat()`)
or by `as.break()` call. Normal termination is seen as as.success() call.

Abnormal termination is possible through `as.error()`, including timeout, or external `as.cancel()`.
Abnormal termination is seen as `as.error()` call.


## 1.9. The Safety Rules of libraries with AsyncSteps interface

It is possible to split a single step into several functional fragments. In this case, the
topmost function is assumed the one passed to `as.add()` directly.

1. `as.success()` should be called only in the topmost function of the step.
1. `as.setCancel()` and/or `as.setTimeout()` must be called only in the topmost function
    as repeated calls override those in the scope of the step.
1. Library entry points on project boundaries should call `as.add()` internally for any
    operation with side effects to ensure correct order of operations.

## 1.10. Reserved keyword name clash

If any of API identifiers clashes with one of reserved words or has illegal symbols then
implementation-defined name mangling is allowed, but with the following guidelines
in priority.

Pre-defined alternative method names, if the default matches language-specific reserved keywords:

* *loop* -> makeLoop
* *forEach* -> loopForEach
* *repeat* -> repeatLoop
* *break* -> breakLoop
* *continue* -> continueLoop
* Otherwise, - try adding underscore to the end of the
    identifier (e.g. do -> do_)

## 1.11. Synchronization

### 1.11.1. Mutual exclusion

As with any multi-threaded application, multi-step cases may also require synchronization
to ensure not more than N steps enter the same critical section which spans over several
fragments (steps) of the asynchronous flow.

Implemented as `Mutex` class.

### 1.11.2. Throttling

For general stability reasons and protection of self-DoS, it may be required to limit
number of steps allowed to enter critical section within time period.

Implemented as `Throttle` class.

### 1.11.3. API details

A special `as.sync(obj, step, err_handler)` API is available to synchronize against
any object supporting synchronization protocol `as.sync(as, step, err_handler)`.

Synchronization object is allowed to add own steps and is responsible for adding
request steps under protection of provided synchronization. Synchronization object
must correctly handle canceled execution and possible errors.

Incoming success parameters must be passed to critical section step.
Resulting success parameters must be forwarded to the following steps like there is
no critical section logic.

### 1.11.4. Reentrance requirements

All synchronization implementations must either allow multiple reentrance of the
same AsyncSteps instance or properly detect and raise error on such event.

All implementations must correctly detect parallel flows in the scope of a single AsyncSteps
instance and treat each as a separate one. None of paralleled steps should inherit
the lock state of its parent step.

### 1.11.5. Deadlock detection

Deadlock detection is optional and is not mandatory required.

### 1.11.6. Max queue limits

It may be required to limit maximum number of pending AsyncSteps flows. If overall
queue limit is reached then new entries must get "DefenseRejected" error.

### 1.11.7. Processing limits

Request processing stability requires to limit both simultaneous connections and
request rate. Therefore a special synchronization primitive `Limiter` wrapping
`Mutex` and `Throttle` is introduced to impose limits in scope.

### 1.12. Success step and result injection

Sometimes, it's required to return a value after inner steps are executed. It leads
to code like:

```
    value = 123;
    as.add( subStep() );
    as.add( (as) => as.success( value ) );
```

To optimize and make the code cleaner previously deprecated `as.successStep()` is
returned. Example:

```
    value = 123;
    as.add( subStep() );
    as.successStep( value );
```

### 1.13. Promise/await integration

As Promises and `await` patterns become more and more popular in modern technologies,
AsyncSteps should support them through `as.await(future_or_promise)` call.

Details of implementation is specific to particular technology. However, the following
guidelines should be used:

1. Async step must be added.
1. If `future_or_promise` is cancellable then `as.setCancel()` must be used.
1. Otherwise, `as.waitExternal()` to be used.
1. Errors must be propagated through `as.error()`
1. Result must be propagated through `as.success()`

### 1.14. Allocation for technologies without garbage collected heap

For most GC-based technologies step closures can use objects allocated in outer steps
without issues. However, object lifetime management is important for technologies like ISO C++.

A special `Pointer stack(size)` execution API is provided. The raw version acts like
regular heap allocation, but allocated memory is automatically freed once step is destroyed.

If other lifetime is required then implementation-specific shared pointers should be used.

Technology-specific implementation should provide template or generic overload to better
integrate with specific type system and other features. Example:

    // Prototype
    template<typename T, typename... Args>
    T& stack(Args&&... args);
    
    // to be used like
    asi.stack<T>();
    asi.stack<T>(SomeCtorParam);


# 2. Async Steps API

## 2.1. Types

* `void execute_callback( AsyncSteps as[, previous_success_args] )`:
    * the first argument is always AsyncSteps object;
    * other arguments come from the previous as.success() call, if any;
    * returns nothing;
    * behavior:
        * either set completion status through `as.success()` or `as.error()`,
        * or add sub-steps through `as.add()` and/or `as.parallel()`,
        * Optionally, set set time limit through `as.setTimeout()` and/or
            set cancel handler through `as.setCancel()`,
        * any violation is reported as `as.error( InternalError )`;
    * can use `as.state()` for global current job state data.
* `void error_callback( AsyncSteps as, error )`:
    * the first argument is always AsyncSteps object;
    * the second argument comes from the previous `as.error()` call;
    * returns nothing;
    * behavior, completes through:
        * `as.success()` - continue execution from the next step, after return,
        * `as.error()` - change error string,
        * silent return - continue unwinding error handler stack,
        * any violation is reported as `as.error( InternalError )`.
    * can use `as.state()` for global current job state data.
* `void cancel_callback( AsyncSteps as )`:
    * it must be used to cancel out of AsyncSteps program flow actions, like
        waiting on connection, timer, dedicated task, etc.
* `interface ISync`
    * `void sync( AsyncSteps, execute_callback[, error_callback] )`:
        * synchronized independent or parallel AsyncSteps, execute provided
            callbacks in critical section.

    
## 2.2. Functions

It is assumed that all functions in this section are part of **the single AsyncSteps interface**.
However, they are grouped by semantical scope of use.

### 2.2.1. Common API - can be used in any context

1. `AsyncSteps add( execute_callback func[, error_callback onerror] )`:
    * adds a step, the executor callback gets async interface as the first parameter;
    * can be called multiple times to add sub-steps of the same level (sequential execution);
    * steps are queued in the same execution level (sub-steps create a new level);
    * returns current level `AsyncSteps` object accessor for easy chaining.
1. `AsyncSteps parallel( [error_callback onerror] )`:
    * creates a step and returns specialization of AsyncSteps interface:
        * all `add()`'ed sub-steps are executed in parallel (not strictly required),
        * the next step in the current level is executed only when all parallel steps complete,
        * sub-steps of parallel steps follow normal sequential semantics,
        * `success()` does not allow any arguments - use `state()` to pass results.
1. `Map state()`:
    * returns a reference to map/object, which can be populated with arbitrary state values;
    * note: if boolean cast is not supported in given technology then it should return
        equivalent of `null` to identify invalid state of AsyncSteps object.
1. *get/set/exists/unset* wildcard accessor, which map to state() variables:
    * only if supported by language/platform.
1. `AsyncSteps copyFrom( AsyncSteps other )`:
    * copies steps and state variables not present in the current state
    from other(model) AsyncSteps object;
    * see cloning concept.
1. *clone*/*copy c-tor*
    - implementation-defined way of cloning AsyncSteps object.
1. `AsyncSteps sync(ISync obj, execute_callback func[, error_callback onerror] )`:
    - adds a step, which is synchronized against `obj`.
1. `AsyncSteps successStep( [result_arg, ...] )`:
    - an efficient shortcut for `as.add( (as) => as.success( result_arg, ... ) )`.
1. `AsyncSteps await( future_or_promise[, error_callback onerror] )`:
    - integrate technology-specific Future/Promise as a step.
1. `AsyncSteps newInstance()`:
    - create a new instance of AsyncSteps for standalone execution.
1. `boolean cast()`:
    - true, if AsyncSteps interface is in valid state for usage;
    - if not possible in given technology, then see the `state()` notes.
1. `FutoInAsyncSteps cast()`:
    - cast to binary AsyncSteps interface pointer as applicable in technology;
    - if not possible in given technology, then see the `binary()` notes..
1. `FutoInAsyncSteps binary()`:
    - get naked binary AsyncSteps interface pointer as applicable in technology.
1. `AsyncSteps wrap(FutoInAsyncSteps)`:
    - adopt the binary interface pointer as applicable;
    - if the binary interface is implemented by the same technology then
        it should be a simple cast;
    - otherwise, foreign implementation should be seamlessly wrapped;
    - returned instance must be used, but not the one on which `wrap()` is being called.

### 2.2.2. Execution API - can be used only inside execute_callback

*Note: `success()` and `error()` can be used in error_callback as well*

1. `void success( [result_arg, ...] )`
    * successfully completes the current step's execution;
    * it should be normally called from `execute_callback`;
    * however, it can be called outside of `AsyncSteps` stack during external event waiting.
1. `void error( name [, error_info] )`:
    * completes the step with error;
    * throws `FutoIn.Error` exception immediately;
    * calls `onerror( async_iface, name )` after returning to execution engine;
    * `error_info`- assigned to `error_info` state field.
1. `void setTimeout( timeout_ms )`:
    * disables implicit success with assumption of external event waiting, if no sub-steps are added;
    * on timeout, `Timeout` error is raised.
1. `call operator overloading`:
    * if supported by language/platform, it is an alias for `as.success()`.
1. `void setCancel( cancel_callback oncancel )`:
    * set the callback, to be used to cancel execution.
1. `void waitExternal()`:
    * prevent implicit `as.success()` behavior of the current step.
1. `Pointer stack(size[, destroy_cb])`:
    * allocate a temporary object with lifetime of the current step for non-GC technologies.

### 2.2.3. Control API - can be used only on Root AsyncSteps objects

1. `void execute()` - must be called only once after root object steps are configured.
    * Initiates AsyncSteps execution implementation-defined way.
1. `void cancel()` - may be called on root object to asynchronously cancel execution.
    * Cancellation typically happens on continuation of `AsyncSteps` execution.
1. `Promise promise()` - must be called only once after the root object steps are configured.
    * Wraps `execute()` into a native Promise object.
    * Returns a native Promise object.

### 2.2.4. Execution Loop API - can be used only inside `execute_callback`

1. `void loop( func, [, label] )`:
    * executes the loop until `as.break()` is called;
    * `func( as )` - the loop body;
    * `label` - am optional label to use for `as.break()` and `as.continue()` in inner loops.
1. `void forEach( map|list, func [, label] )`:
    * for each `map` or `list` element, call `func( as, key, value )`;
    * `func( as, key, value )` - the loop body;
    * `label` - an optional label to use for `as.break()` and `as.continue()` in inner loops.
1. `void repeat( count, func [, label] )`:
    * calls `func(as, i)` for `count` times;
    * `count` - how many times to call the `func`;
    * `func( as, i )` - the loop body, i - current iteration starting from `0`;
    * `label` - an optional label to use for `as.break()` and `as.continue()` in inner loops.
1. `void break( [label] )`:
    * breaks execution of current loop;
    * also raises a special exception which gets handled by `AsyncSteps` internally;
    * `label` - unwinds nested loops, until `label` named loop is exited.
1. `void continue( [label] )`:
    * continue loop execution from the next iteration;
    * also raises a special exception which gets handled by `AsyncSteps` internally;
    * `label` - break nested loops, until `label` named loop is found.

### 2.3. `Mutex` class

* It must implement `ISync` interface.
* Functions:
    * `c-tor(unsigned integer max=1, unsigned integer max_queue=null)`:
        * sets the maximum number of parallel AsyncSteps entering the critical section;
        * `max_queue` - optionally, limit the queue length.

### 2.4. `Throttle` class

* It must implement `ISync` interface.
* Functions:
    * `c-tor(unsigned integer max, unsigned integer period_ms=1000, unsigned integer max_queue=null)`:
        * sets the maximum number of the critical section entries within the given time period;
        * `period_ms` - the time period in milliseconds;
        * `max_queue` - optionally, limit the queue length.

### 2.5. `Limiter` class

* It must implement `ISync` interface.
* Functions:
    * `c-tor(options)`:
        * Complex limit handling;
        * `options.concurrent=1` - the number maximum of concurrent flows;
        * `options.max_queue=0` - the number maximum of queued flows;
        * `options.rate=1` - the number maximum of the critical section entries in the given period;
        * `options.period_ms=1000` - the time period in milliseconds;
        * `options.burst=0` - the number maximum of queued flows for rate limiting.

### 2.6. AsyncTool event loop interface

There is a strong assumption that AsyncSteps instances are executed in partial order by a common
instance of event loop, with a historical name AsyncTool.

There is an assumption that AsyncTool will be extended with Input/Output event support to act
as a true reactor, but it may not be always possible.

AsyncTool was not defined in previous versions of the specification while it was always existing
because its interface is specific to technology. Below is only **a general suggestion**.

1. `Handle immediate( func )`:
    - schedule an immediate callback;
    - `func()` - general callback.
1. `Handle deferred( delay, func )`:
    - schedule a callback with delay;
    - `delay` - typically time period in milliseconds;
    - `func()` - general callback.
1. `bool is_same_thread()`:
    - check if current operating system thread is the same as the internal event loop's one;
    - if applicable at all.
1. `void cancel( handle )`:
    - cancel a previously scheduled callback;
    - it should not be an error, if callback has been already executed;
    - this method may be a part of the `Handle` object's interface.
1. `void is_valid( handle )`:
    - an ability to check if the handle still refers to scheduled task;
    - this method may be a part of the `Handle` object's interface.

### 2.7. Universal binary interface

To achieve the initial goal of the FutoIn project - universal cross-technology interface, a certain
minimal binary interface has to be defined to be passed as an ordinary memory pointer for the first
parameter of callback functions, so any technology-specific solution could wrap that as necessary and
allow mixing asynchronous step fragments written in different languages like C, C++, C#, ECMAScript,
Java, Lua, Ruby, Rust and others in scope of a single asynchronous thread.

As the base idea, Java Native Interface approach is taken, where a pointer to an abstract plain structure
is passed. The first field of such structure is a pointer to a table of plain C functions, each API
functions also assumes to get the pointer to the structure as the first parameter. C++ virtual table
is also working similar way.

Plain ISO C is supported one way or another in almost every technology to create bindings and other type
of glue functionality. Therefore, it is used to describe the binary interface with assumption of
only standard platform-defined paddings and pointer sizes while all API callbacks use the standard
platform-defined calling convention.

There are certain limitations as it is problematic to guarantee type safety without significant overhead,
so binary interface user must be more aware of what is being done. State access is split into two API
functions which operate over abstract `void` pointers.

#### 2.7.1. Binary data

Binary data interface is used to pass `execute_callback` arguments between technologies. Directly
are supported:

1. all ISO C primitive integers, floating point and boolean types,
1. single dimension dynamic arrays(vectors) of such types,
1. 8-, 16- and 32-bit Unicode strings,
1. custom technology-specific types.

For efficiency reasons, complex types like vectors may be stored both in agnostic C format and
as a technology-specific object instance. Therefore, binary value holding object supports
cleanup callbacks to properly destroy such objects even from C or Assembly code.

``` c
typedef struct FutoInBinaryValue_ FutoInBinaryValue;
typedef struct FutoInType_ FutoInType;
typedef uint8_t FutoInTypeFlags;

enum
{
    FTN_TYPE_CUSTOM_OBJECT = 0x01,
    FTN_TYPE_STRING = 0x02,
    FTN_TYPE_STRING16 = 0x03,
    FTN_TYPE_STRING32 = 0x04,
    FTN_TYPE_BOOL = 0x05,
    FTN_TYPE_INT8 = 0x06,
    FTN_TYPE_INT16 = 0x07,
    FTN_TYPE_INT32 = 0x08,
    FTN_TYPE_INT64 = 0x09,
    FTN_TYPE_UINT8 = 0x0A,
    FTN_TYPE_UINT16 = 0x0B,
    FTN_TYPE_UINT32 = 0x0C,
    FTN_TYPE_UINT64 = 0x0D,
    FTN_TYPE_FLOAT = 0x0E,
    FTN_TYPE_DOUBLE = 0x0F,
    FTN_BASE_TYPE_MASK = 0x0F,
    // --
    FTN_TYPE_ARRAY = 0x10,
    FTN_COMPLEX_TYPE_MASK = 0xF0,
};

struct FutoInType_
{
    const FutoInTypeFlags flags;
    void (*const cleanup)(FutoInBinaryValue* v);
    // NOTE: extendable by implementation
};

struct FutoInBinaryValue_
{
    const FutoInType* type;
    union
    {
        const void* p;
        const char* cstr;
        const char16_t* cstr16;
        const char32_t* cstr32;
        bool b;
        int8_t i8;
        int16_t i16;
        int32_t i32;
        int64_t i64;
        uint8_t u8;
        uint16_t u16;
        uint32_t u32;
        uint64_t u64;
        float f;
        double d;
    };
    void* custom_data;
    uint32_t length;
};

static inline void futoin_reset_binval(FutoInBinaryValue* v)
{
    auto tp = v->type;
    if (tp) {
        auto* f = tp->cleanup;
        if (f) {
            f(v);
        }
    }

    v->type = 0;
    v->u64 = 0;
    v->custom_data = 0;
    v->length = 0;
}
```

#### 2.7.2. Binary AsyncSteps interface

Binary interface has a maximum limit of 4 custom arguments according to the industry best practices.
Thefore, argument object is a collection of 4 binary value holders.

Binary interface is inspired by a typical C++ vtable and Java Native Interface specification.
It is assumed that a pointer to an agnostic `FutoInAsyncSteps` structure is passed instead
of technology-specific interface object. Such structure has the first field of a pointer to a function
table. Each function receives the same pointer to the structure as the first argument. There may
be additional implementation-defined fields. Therefore, business logic code must not assume that
it knows actual size of such structure.

Unlike most of traditional cases, ISO C11 does not support exceptions and that imposes some restrictions
and duties for business logic. For example, raising errors requires returning from the handler function
manually.

The meaning of functions is the same, except additional `data` and similar arguments may be added to
bind dynamic data to callbacks user-defined way.

The function table is also extended with AsyncTool interface for convenience.

``` c
typedef struct FutoInAsyncStepsAPI_ FutoInAsyncStepsAPI;
typedef struct FutoInAsyncSteps_ FutoInAsyncSteps;
typedef struct FutoInSyncAPI_ FutoInSyncAPI;
typedef struct FutoInSync_ FutoInSync;
typedef struct FutoInArgs_ FutoInArgs;
typedef struct FutoInHandle_ FutoInHandle;

struct FutoInArgs_
{
    union
    {
        struct
        {
            FutoInBinaryValue arg0;
            FutoInBinaryValue arg1;
            FutoInBinaryValue arg2;
            FutoInBinaryValue arg3;
        };
        FutoInBinaryValue args[4];
    };
};

struct FutoInHandle_
{
    void* data1;
    void* data2;
    ptrdiff_t data3;
};

typedef void (*FutoInAsyncSteps_execute_callback)(
        FutoInAsyncSteps* bsi, void* data, const FutoInArgs* args);
typedef void (*FutoInAsyncSteps_error_callback)(
        FutoInAsyncSteps* bsi, void* data, const char* code);
typedef void (*FutoInAsyncSteps_cancel_callback)(
        FutoInAsyncSteps* bsi, void* data);

struct FutoInAsyncStepsAPI_
{
    union
    {
        struct
        {
            // Index 0
            void (*add)(
                    FutoInAsyncSteps* bsi,
                    void* data,
                    FutoInAsyncSteps_execute_callback f,
                    FutoInAsyncSteps_error_callback eh);
            // Index 1
            FutoInAsyncSteps* (*parallel)(
                    FutoInAsyncSteps* bsi,
                    void* data,
                    FutoInAsyncSteps_error_callback eh);
            // Index 2
            void* (*stateVariable)(
                    FutoInAsyncSteps* bsi,
                    void* data,
                    const char* name,
                    void* (*allocate)(void* data),
                    void (*cleanup)(void* data, void* value));
            // Index 3
            void* (*stack)(
                    FutoInAsyncSteps* bsi,
                    size_t data_size,
                    void (*cleanup)(void* value));
            // Index 4
            void (*success)(FutoInAsyncSteps* bsi, FutoInArgs* args);
            // Index 5
            void (*handle_error)(
                    FutoInAsyncSteps* bsi, const char* code, const char* info);
            // Index 6
            void (*setTimeout)(FutoInAsyncSteps* bsi, uint32_t timeout_ms);
            // Index 7
            void (*setCancel)(
                    FutoInAsyncSteps* bsi,
                    void* data,
                    FutoInAsyncSteps_cancel_callback ch);
            // Index 8
            void (*waitExternal)(FutoInAsyncSteps* bsi);
            // Index 9
            void (*loop)(
                    FutoInAsyncSteps* bsi,
                    void* data,
                    void (*f)(FutoInAsyncSteps* bsi, void* data),
                    const char* label);
            // Index 10
            void (*repeat)(
                    FutoInAsyncSteps* bsi,
                    void* data,
                    size_t count,
                    void (*f)(FutoInAsyncSteps* bsi, void* data, size_t i),
                    const char* label);
            // Index 11
            void (*breakLoop)(FutoInAsyncSteps* bsi, const char* label);
            // Index 12
            void (*continueLoop)(FutoInAsyncSteps* bsi, const char* label);
            // Index 13
            void (*execute)(
                    FutoInAsyncSteps* bsi,
                    void* data,
                    FutoInAsyncSteps_error_callback unhandled_error);
            // Index 14
            void (*cancel)(FutoInAsyncSteps* bsi);
            // Index 15
            void (*addSync)(
                    FutoInAsyncSteps* bsi,
                    FutoInSync* sync,
                    void* data,
                    FutoInAsyncSteps_execute_callback f,
                    FutoInAsyncSteps_error_callback eh);
            // Index 16
            ptrdiff_t (*rootId)(FutoInAsyncSteps* bsi);
            // Index 17
            int (*isValid)(FutoInAsyncSteps* bsi);
            // Index 18
            FutoInAsyncSteps* (*newInstance)(FutoInAsyncSteps* bsi);
            // Index 19
            void (*free)(FutoInAsyncSteps* bsi);
            // Index 20
            FutoInHandle (*sched_immediate)(
                    FutoInAsyncSteps* bsi, void* data, void (*cb)(void* data));
            // Index 21
            FutoInHandle (*sched_deferred)(
                    FutoInAsyncSteps* bsi,
                    uint32_t delay_ms,
                    void* data,
                    void (*cb)(void* data));
            // Index 22
            void (*sched_cancel)(FutoInAsyncSteps* bsi, FutoInHandle* handle);
            // Index 23
            int (*sched_is_valid)(FutoInAsyncSteps* bsi, FutoInHandle* handle);
            // Index 24
            int (*is_same_thread)(FutoInAsyncSteps* bsi);
        };
        void* funcs[25];
    };
    // NOTE: extendable by implementation
};
struct FutoInAsyncSteps_
{
#ifdef __cplusplus
    FutoInAsyncSteps_(const FutoInAsyncStepsAPI* api) noexcept : api(api) {}
#endif
    const FutoInAsyncStepsAPI* const api;
    // NOTE: extendable by implementation
};
```

#### 2.7.3. Binary synchronization primitive's interface

Synchronization object interface is defined separately from the AsyncSteps one as
it is quite possible that AsyncSteps may be implemented in one technology while the
synchronization object is implemented in an absolutely different one.

``` c
struct FutoInSyncAPI_
{
    union
    {
        struct
        {
            // Index 0
            void (*lock)(FutoInAsyncSteps* bsi, FutoInSync* sync);
            // Index 1
            void (*unlock)(FutoInAsyncSteps* bsi, FutoInSync* sync);
        };
        void* funcs[2];
    };
    // NOTE: extendable by implementation
};
struct FutoInSync_
{
#ifdef __cplusplus
    FutoInSync_() noexcept : api(nullptr) {}
#endif
    const FutoInSyncAPI* const api;
    // NOTE: extendable by implementation
};
```

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
        },
    )
    
## 3.3. parallel() steps and state()

    AsyncStepsImpl as;

    as.add(
        function( inner_as ){
            inner_as.parallel().add(
                function( inner2_as ){
                    inner2_as.state().parallel_1 = 1;
                },
                function( inner2_as, error )
                {
                    log( "Spotted error " + error )
                    // continue with higher level error handlers
                }
            ).add(
                function( inner2_as ){
                    inner2_as.state().parallel_2 = 2;
                },
                function( inner2_as, error )
                {
                    inner2_as.state().parallel_2 = 0;
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
        },
    )
    
## 3.4. loops

    AsyncStepsImpl as;
    
    as.add(
        function( as ){
            as.repeat( 3, function( as, i ) {
                print i;
            } );
            
            as.forEach( [ 1, 3, 3 ], function( as, k, v ) {
                print k "=" v;
            } );
            
            as.forEach( as.state(), function( as, k, v ) {
                print k "=" v;
            } );
        },
    )
    
## 3.5. External event wait

    AsyncStepsImpl as;
    
    as.add(
        function( as ){
            as.waitExternal();
            
            callSomeExternal( function(err) {
                if (err)
                {
                    try {
                        as.error(err);
                    } catch {
                        // ignore
                    }
                }
                else
                {
                    as.success();
                }
            } );
        },
    )
    
## 3.6. Synchronization

    AsyncStepsImpl as;
    MutexImpl mutex(10);
    
    as.sync(
        mutex,
        function( as ){
            // critical section with regular AsyncSteps
        },
    )
        
    
=END OF SPEC=
