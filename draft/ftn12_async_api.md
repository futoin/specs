<pre>
FTN12: FutoIn Async API
Version: 1.15DV
Date: 2026-08-11
Copyright: 2014-2026 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.15 - 2026-08-11 - Andrey Galkin
    * NEW: asi.errorNoThrow() API
    * CHANGED: revised the spec text, also with meaningful changes:
        - deprecated the `asi.copyFrom()` idea;
        - relaxed requirement for inheritance support of the AsyncSteps;
        - corrected the examples;
        - the library safety rules are rewritten;
        - formalized `State` interface convention;
        - removed never implemented state variable accessors on the AsyncSteps;
        - removed enver implemented clone/copy c-tors;
        - clarified the assumption for a sane 4 result argument limit.
* v1.14.1 - 2026-07-27 - Andrey Galkin
    * FIXED: is_valid() return type
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

This interface was initially born as a secondary option for the FTN6 Executor
concept. However, it quickly became clear that async, reactor, proactor, light
threads, etc. should be the base of scalable high performance server
implementations and light clients, even though it is sometimes more difficult
for understanding and/or debugging. Later that has been confirmed multiple times
with all sorts of modern async functionality, including its iconic `async/await`
pattern. The traditional synchronous program flow becomes an addon on top of
asynchronous base for legacy code and/or too complex logic. Academic and
practical research in this direction was started in field of cooperative
multitasking back in XX century.

Program flow is split into non-blocking execution steps, represented
with execution callback function. Processing Unit (eg. CPU) halting/
spinning/switching-to-another-task is seen as a blocking action in program flow.
Execution of such fragments is partially ordered.

Any step must not call any of blocking functions, except for synchronization
with guaranteed minimal period of lock acquisition. *Note: under minimal period,
it is assumed that any acquired lock is immediately released after action with
O(1) complexity and no delay caused by programmatic suspension/locking of the
executing task.*

Every step is executed sequentially. A successful result of any step becomes the
input for the following step.

Each step can have own error handler. Error handler is called, if
`AsyncSteps.error()` is called within step execution or any of its sub-steps.
A typical behavior of such handler is to override the error and to continue, or
to make cleanup actions and complete job with the error still pending.

Each step can have own sequence of sub-steps. Sub-steps can be added only during
that step execution. Sub-step sequence is executed after current step execution
is finished.

If there are any sub-steps added then the current step must not call
`AsyncSteps.success()` or `AsyncSteps.error()`. Otherwise, `InternalError`
is raised.

It is possible to create a special "parallel" sub-step and add independent
sub-steps to it. Execution of each parallel sub-step is start interleaved way.
The parallel step completes with success when all sub-steps complete
successfully. If error is raised in any sub-step of the parallel step then all
other sub-steps are canceled.

Out-of-order cancel of execution can occur by a timeout, execution control
engine decision (e.g. Invoker disconnect), or a failure in the sibling parallel
steps. Each step can install custom on-cancel handler to free up resources
and/or cancel external jobs. After cancel, it must be safe to destroy the
AsyncSteps object.

AsyncSteps must be used in Executor request processing. The same [root]
AsyncSteps object must be used for all asynchronous tasks within a given request
processing.

AsyncSteps may be used by the FTN7 Invoker implementation.

AsyncSteps may support derived classes in implementation-defined way.
A typical use case: functionality extension (e.g. request processing API).

For performance reasons, it is may be more efficient to initialize AsyncSteps
with many business logic steps platform-specific AsyncSteps cloning/duplicating,
but this ideas has not really much use and is deprecated now.

## 1.1. Levels

When AsyncSteps (or derived) object is created all steps are added sequentially
in the Level 0 through the `add()`, `parallel()` or loop API. *Note: each
`parallel()` is seen as a step.*

After AsyncSteps execution is initiated, each step of the Level 0 is executed.
All sub-steps are added in the Level n+1. Example:

    add() -> Level 0 #1
        add() -> Level 1 #1
            add() -> Level 2 #1
            parallel().add() -> Level 2 #2
            add() -> Level 2 #3
        parallel().add() -> Level 1 #2
        add() -> Level 1 #3
    parallel() -> Level 0 #2
    add() -> Level 0 #3

    
Execution cannot continue to the next step of the current Level until all
sub-steps of nested levels are executed.

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

## 1.2. Error Handling

Due to nonlinear programming, classic try/catch blocks are converted into
execute-onerror pairs. Each added step may have its custom error handler. If
such error handler is not specified then the control is passed to lower Level
error handler. If none is defined then execution is aborted.

Example:

    add( -> Level 0
        func( asi ){
            print( "Level 0 func" )
            add( -> Level 1
                func( asi ){
                    print( "Level 1 func" )
                    asi.error( "myerror" )
                },
                onerror( asi, error ){
                    print( "Level 1 onerror: " + error )
                    asi.error( "newerror" )
                }
            )
        },
        onerror( asi, error ){
            print( "Level 0 onerror: " + error )
            asi.success( "Prm" )
        }
    )
    add( -> Level 0
        func( asi, param ){
            print( "Level 0 func2: " + param )
            asi.success()
        }
    )


The output would be:

    Level 0 func
    Level 1 func
    Level 1 onerror: myerror
    Level 0 onerror: newerror
    Level 0 func2: Prm
    
In a synchronous way, it would look like:

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

## 1.2.1. Steps in Error Handlers

Very often, error handler creates an alternative complex program path which
requires own async operation. Therefore, such error handler must accept
`asi.add()` as an implicit `asi.success()` override.

If steps are added inside error handler they must remain on the same async stack
level while error handler itself gets removed.

Example:

    add( -> Level 0
        func( asi ){
            print( "Level 0 func" )
            add( -> Level 1
                func( asi ){
                    print( "Level 1 func" )
                    asi.error( "first" )
                },
                onerror( asi, error ){
                    print( "Level 1 onerror: " + error )
                    asi.add( -> Level 2
                        func() {
                            print( "Level 2 func" )
                            asi.error( "second" );
                        },
                        onerror( asi, error ) {
                            print( "Level 2 onerror: " + error )
                        }
                    )
                }
            )
        },
        onerror( asi, error ){
            print( "Level 0 onerror: " + error )
        }
    )


The output would be:

    Level 0 func
    Level 1 func
    Level 1 onerror: first
    Level 2 func
    Level 2 onerror: second
    Level 0 onerror: second

*Note: the "Level 1 onerror" is not executed second time!*

## 1.3. Wait for External Resources

Very often, execution of step cannot continue without waiting for some external
event, like input from network or disk. It is forbidden to block execution in
such event waiting. As a solution, there are special `setTimeout()` and
`setCancel()` API methods.

Example:

    add(
        func( asi ){
            socket.read( function( data ){
                asi.success( data )
            } )
            
            asi.setCancel( function(){
                socket.cancel_read()
            } )
            
            asi.setTimeout( 30_000 ) // 30 seconds
        },
        onerror( asi, error ){
            if ( error == timeout ) {
                print( "Timeout" )
            }
            else
            {
                print( "Read Error" )
            }
        }
    )

## 1.4. Abort in Parallel Execution

The definition of the parallel steps aborts execution, if any of the pallel
steps fails. To avoid excessive time and resources spent on other steps, there
is a concept of canceling sibling steps execution similar to the timeout above.

Example:
    
    asi.parallel()
        .add(
            func( asi ){
                asi.setCancel( function(){ ... } )
                
                // do parallel job #1
                asi.state()->result1 = ...;
            }
        )
        .add(
            func( asi ){
                asi.setCancel( function(){ ... } )

                // do parallel job #1
                asi.state()->result2 = ...;
            }
        )
        .add(
            func( asi ){
                asi.error( "Some Error" )
            }
        )
    asi.add(
        func( asi ){
            print( asi.state()->result1 + asi.state->result2 )
            asi.success()
        }
    )

## 1.5. AsyncSteps Cloning

This is a deprecated concept, which can be used in some only niche
optimizations. Therefore, it may not be supported in all implementations.

In long living applications the same business logic may be reused multiple
times during execution. This applies only to same level sub-steps.

In a REST API server example, complex business logic can be defined only once
and stored in a kind of AsyncSteps object repository. On each request, a
reference object from the repository would be copied for actual processing with
minimal overhead for sub-steps initialization.

However, there would be no-to-little performance difference in sub-step
definition unless its callback function is also created at initialization time,
but not at parent step execution time (the default concept). So, it should be
possible to predefine those as well and copy during step execution. Copying
steps must also involve copying of the state variables, which are not set in the
target state.

Example:

    AsyncSteps req_repo_common;
    req_repo_common.add(func( asi ){
        asi.add( func( asi ){ ... } );
        asi.copyFrom( asi.state().business_logic );
        asi.add( func( asi ){ ... } );
    });
    
    AsyncSteps req_repo_buslog1;
    req_repo_buslog1
        .add(func( asi ){ ... })
        .add(func( asi ){ ... });

    AsyncSteps actual_exec = copy req_repo_common;
    actual_exec.state().business_logic = req_repo_buslog1;
    actual_exec.execute();

However, this approach only makes sense for deep performance optimizations.

## 1.6. Implicit `asi.success()`

If there are no sub-steps added, no timeout set and no cancel handler set then
implicit `asi.success()` call is assumed to simplify code and increase
efficiency of steps execution. However, such approach does not apply to the 
error handlers!

    asi.add(func( asi ){
        doSomeStuff( asi );
    })

## 1.6.1. `asi.waitExternal()` Shortcut for Empty Cancellation Handler

As in many cases it's required to wait for external event without any additional
conditions, the general approach appeared to be adding an empty cancel handler.
To avoid that, an explicit `asi.waitExternal()` API is provided.

## 1.7. Error Info, Last Exception and Async Call Stack

Predefined state variables:

* **error_info** - a value of the second parameter passed to the last
  *as.error()* call.
* **last_exception** - the last exception caught, if feasible to implement.
* **async_stack** - implementation-defined stack of step handler references.

Implementation may replace state variables with specific State object API.

The error code is not always descriptive enough, especially, if it can be
generated in multiple places. As a convention, special `error_info` state field
should hold descriptive information of the last error. Therefore, `asi.error()`
is extended with optional parameter `error_info`.

The `last_exception` state variables may hold the last exception object caught,
if feasible to implement. It should be populated with thrown FutoIn error
objects as well.

## 1.8. Async Loops

Almost always, program flow is nonlinear, and loops are required.

Basic princips of the async loops:

        asi.loop( func( asi ){
            call_some_library( asi );
            asi.add( func( asi, result ){
                if ( !result )
                {
                    // exit loop
                    asi.break();
                }
            } );
        } )

Inner loops and identifiers:

        // start loop
        asi.loop( 
            func( asi ){
                asi.loop( func( asi ){
                    call_some_library( asi );
                    asi.add( func( asi, result ){
                        if ( !result )
                        {
                            // exit loop
                            asi.continue( "OUTER" );
                        }

                        asi.success( result );
                    } );
                } );
                
                asi.add( func( asi, result ){
                    // use it somehow
                    asi.success();
                } );
            },
            "OUTER"
        )

Loop `n` times.

        asi.repeat( 3, func( asi, i ){
            print( 'Iteration: ' + i )
        } )

Traverse through a list:

        asi.forEach(
            [ 'apple', 'banana' ],
            func( asi, index, v ){
                print( index + ". " + v )
            }
        )

Traverse through a map:

        asi.forEach(
            [ 'apple', 'banana' ],
            func( asi, k, v ){
                print( k + " = " + v )
            }
        )


### 1.8.1. Termination

Normal loop termination is performed either by a loop condition (e.g.
`asi.forEach()`, `asi.repeat()`) or by `asi.break()` call. Normal termination is
 seen as an implicit `asi.success()` call.

Abnormal termination is possible through `asi.error()`, including timeout, or
external `asi.cancel()`. Abnormal termination is seen as a `asi.error()` call.


## 1.9. The Safety Rules of Libraries with AsyncSteps Interface

A good library calling convention has never been provided, and each use case in
the field is unique. The following recommendations are provided, begging with
FTN12 v1.15.

1. The current level AsyncSteps must be passed to the library API directly.
1. The library can add own sub-steps to the current outer step.
1. The library should use `asi.successStep()` to return any variables.
1. The library must not interfere with the outer step execution otherwise,
   including:
    - `asi.setCancel()`, `asi.setTimeout()` and `asi.waitExternal` must only be
      called in the sub-steps added by the library function;
    - the library entry points on project boundaries should call `as.add()`
    internally for any operation with side effects to ensure correct order of
    operations.

The library calls inside the current project boundaries may deviate from such
guidelines for efficiency of operations.

## 1.10. Reserved Keyword Name Clash

If any of API identifiers clashes with one of reserved words or has illegal
symbols then implementation-defined name mangling is allowed, but with the
following guidelines in priority.

Predefined alternative method names, if the default matches language-specific
reserved keywords:

* *loop* -> makeLoop
* *forEach* -> loopForEach
* *repeat* -> repeatLoop
* *break* -> breakLoop
* *continue* -> continueLoop
* Otherwise, - try adding underscore to the end of the identifier (e.g. do ->
  do_).

## 1.11. Synchronization

Although AsyncSteps are designed for single-thread operation, synchronization
between executing instances is still necessary.

### 1.11.1. Mutual exclusion

As with any multi-threaded application, multistep cases may also require
synchronization to ensure that no more than N steps enter the same critical
section which spans over several fragments (steps) of the asynchronous flow.

Implemented as `Mutex` class.

### 1.11.2. Throttling

For general stability reasons and protection of self-DoS, it may be required to limit
number of steps allowed to enter a critical section within time period.

Implemented as `Throttle` class.

### 1.11.3. API details

A special `asi.sync(obj, step, err_handler)` shortcut API is available to
synchronize against any object supporting synchronization protocol with pattern
`obj.sync(asi, step, err_handler)`.

Synchronization object is allowed to add own steps and is responsible for adding
the requested sub-steps under protection of the provided synchronization.
Synchronization object must correctly handle canceled execution and possible
errors.

Incoming success parameters must be passed to the critical section step.
Resulting success parameters must be forwarded to the following steps like there
is no critical section logic.

### 1.11.4. Re-Entrance Requirements

All synchronization implementations must either allow multiple re-entrance of
the same AsyncSteps instance or properly detect and raise error on such event.

All implementations must correctly detect parallel flows in the scope of a
single AsyncSteps instance and treat each as a separate one. None of paralleled
steps should inherit the lock state of its parent step.

### 1.11.5. Deadlock Detection

Deadlock detection is optional and is not mandatory required.

### 1.11.6. Max Queue Limits

It may be required to limit the maximum number of pending AsyncSteps flows. If
overall queue limit is reached then new entries must get the predefined
"DefenseRejected" error.

### 1.11.7. Processing Limits

Request processing stability requires to limit both simultaneous connections and
request rate. Therefore, a special synchronization primitive `Limiter` wrapping
`Mutex` and `Throttle` is introduced to impose combined limits.

### 1.12. Success Step and Result Injection

Sometimes, it's required to return a value after inner steps are executed. It leads
to code like:

```
    value = 123;
    asi.add( subStep );
    asi.add( ( asi ) => asi.success( value ) );
```

To optimize and make the code cleaner, the previously deprecated
`asi.successStep()` is returned. Example:

```
    value = 123;
    asi.add( subStep );
    asi.successStep( value );
```

### 1.13. Promise/Await Integration

As Promises and `await` patterns become more and more popular in modern
technologies, AsyncSteps should support them through
`asi.await(future_or_promise)` call as feasible to implement.

Details of implementation is specific to particular technology. However, the
following guidelines should be used:

1. An async step must be added.
1. If `future_or_promise` is cancellable then `asi.setCancel()` must be used.
1. Otherwise, `asi.waitExternal()` to be used.
1. Errors must be propagated through `asi.error()`
1. Result must be propagated through `asi.success()`

### 1.14. Allocation for Technologies Without Garbage Collected Heap

For most GC-based technologies step closures can use objects allocated in outer
steps without issues. However, object lifetime management is important for
technologies like ISO C++.

A special `Pointer stack(size)` execution API is provided. The raw version acts
like regular heap allocation, but allocated memory is automatically freed once
the step is destroyed.

If other lifetime is required then implementation-specific shared pointers
should be used.

Technology-specific implementation should provide a template or a generic
overload to better integrate with specific type system and other features.
Example:

    // Prototype
    template<typename T, typename... Args>
    T& stack(Args&&... args);
    
    // to be used like
    asi.stack<T>();
    asi.stack<T>(SomeCtorParam);


# 2. Async Steps API

## 2.1. Types

* `void execute_callback( AsyncSteps asi[, previous_success_args] )`:
    * the first argument is always AsyncSteps object;
    * other arguments come from the previous `asi.success()` call, if any;
    * returns nothing;
    * the behavior:
        * either set the completion status through `asi.success()` or
          `asi.error()`;
        * or add sub-steps. including loops;
        * Optionally, set the time limit through `asi.setTimeout()` and/or
            set cancel handler through `asi.setCancel()`,
        * any violation is reported as `asi.error( InternalError )`;
    * can use `asi.state()` for global current job state data.
* `void error_callback( AsyncSteps asi, error )`:
    * the first argument is always AsyncSteps object;
    * the second argument comes from the previous `asi.error()` call;
    * returns nothing;
    * the behavior, completes through:
        * `asi.success()` - continue execution from the next step, after return,
        * `asi.error()` - change error string,
        * a silent return - continue unwinding error handler stack,
        * any violation is reported as `asi.error( InternalError )`.
    * can use `asi.state()` for global current job state data.
* `void cancel_callback( AsyncSteps asi )`:
    * it must be used to cancel out external AsyncSteps program flow actions,
      like waiting on a connection, timer, dedicated task, etc.
* `interface ISync`
    * `void sync( AsyncSteps asi, execute_callback[, error_callback] )`:
        * synchronized independent or parallel AsyncSteps, executes provided
          callbacks in a critical section.
* `interface State`
    * technology-specific;
    * dynamically-typed (e.g. ECMAScript):
        an object or a map of key-values pairs;
    * statically-typed (e.g. C++, Java):
        - `interface CatchTrace` for `callback(exception)` on any caught
          execption;
        - `interface UnhandledError` for `callback(error)` on any unhandled
          FutoIn error in the steps;
        - `Map<String, Object> dynamic_items()` - a map for dynamic variable
            pairs;
        - `get<V>(key)` - get-accessor for dynamic items, type cast;
        - `set<V>(key, value)`- set-accessor for dynamic items, type cast;
        - `error_info` - last `error_info` accessor;
        - `last_exception` - last caught exception;
        - `set_catch_trace()` or `catch_trace` - to setup `CatchTrace` handler;
        - `set_unhandled_error()` or `unhandled_error` - to setup
          `UnhandledError` handler;
        - `mem_pool()` - access associated memory pool, if applicable;

## 2.2. Functions

It is assumed that all functions in this section are part of
**the single AsyncSteps interface**. However, they are grouped by semantic scope
of use. Such design violates certain best practices, but it is done
intentionally.

### 2.2.1. Common API

This API can be used in any context.

1. `AsyncSteps add( execute_callback func[, error_callback onerror] )`:
    * adds a step, the executor callback gets async interface as the first
      parameter;
    * can be called multiple times to add sub-steps of the same level for
      sequential execution;
    * steps are queued in the same execution level;
    * returns the current level `AsyncSteps` object accessor for easy chaining.
1. `AsyncSteps parallel( [error_callback onerror] )`:
    * creates a step and returns a specialization of AsyncSteps interface:
        * all `add()`ed sub-steps are executed in parallel in the same thread,
        * the next step in the current level is executed only when all parallel
          steps complete,
        * sub-steps of parallel steps follow normal sequential semantics,
        * `success()` does not allow any arguments - use either `state()` or
          `stack()` to pass the results.
1. `State state()`:
    * each technology-specific state has own interfaces and semantics;
    * contains a reference to map/object, which can be populated with arbitrary
      state values;    
    * note: if boolean cast is not supported in given technology then it should
      return an equivalent of `null` to identify invalid state of the AsyncSteps
      object.
1. `AsyncSteps copyFrom( AsyncSteps other )`:
    * **deprecated**;
    * copies steps and state variables not present in the current state
      from other(model) AsyncSteps object;
    * see the cloning concept.
1. `AsyncSteps sync(ISync obj, execute_callback func[, error_callback onerror] )`:
    - adds a step, which is synchronized against `obj`.
1. `AsyncSteps successStep( [result_arg, ...] )`:
    - an efficient shortcut for `as.add( (as) => as.success( result_arg, ... ) )`.
1. `AsyncSteps await( future_or_promise[, error_callback onerror] )`:
    - integrate technology-specific Future/Promise as a step.
1. `AsyncSteps newInstance()`:
    - create a new instance of AsyncSteps for standalone execution through
      the agnostic interface with direct dependency on the implementation.
1. `boolean cast()`:
    - true, if AsyncSteps interface is in valid state for usage;
    - if not possible in the given technology then see the `state()` notes.
1. `FutoInAsyncSteps cast()`:
    - cast to binary AsyncSteps interface pointer as applicable in technology;
    - if not possible in the given technology then see the `binary()` notes.
1. `FutoInAsyncSteps binary()`:
    - get a naked binary AsyncSteps interface pointer as applicable in the
      specific technology.
1. `AsyncSteps wrap(FutoInAsyncSteps)`:
    - adopt the binary interface pointer as applicable;
    - if the binary interface is implemented by the same technology then it
      should be a simple cast;
    - otherwise, foreign implementation should be seamlessly wrapped;
    - the returned instance must be used, but not the one on which `wrap()` is
      being called.
    - new returned instance is independent of the current AsyncSteps instance.

### 2.2.2. Execution API

This API can be used only inside the `execute_callback` context. The `success()`
and `error()` can be used in `error_callback` context as well.

1. `void success( [result_arg, ...] )`
    * successfully completes the current step's execution;
    * it should be normally called from `execute_callback`;
    * however, it can be called outside of `AsyncSteps` stack during external
      event waiting;
    * the technology-specific implementation can assume that no more than 4
      result arguments can be supplied as derived from the binary interface.
1. `void error( name [, error_info] )`:
    * completes the step with error;
    * throws `FutoIn.Error` exception immediately;
    * calls `onerror( async_iface, name )` after returning to execution engine;
    * `error_info` is assigned to the `error_info` state field.
1. `void errorNoThrow( name [, error_info] )`:
    * a special variation of the `asi.error()`, which does not throw and the
      user must return from the executing function without relying on the
      exception.
1. `void setTimeout( timeout_ms )`:
    * disables the implicit success with an assumption of external event
      waiting, if no sub-steps are added;
    * on timeout, `Timeout` error is raised.
1. `call operator overloading`:
    * if supported by language/platform, it is an alias for `asi.success()`.
1. `void setCancel( cancel_callback oncancel )`:
    * set the callback, to be used to cancel execution.
1. `void waitExternal()`:
    * prevents the implicit success behavior of the current step.
1. `Pointer stack(size[, destroy_cb])`:
    * allocates a temporary object with lifetime of the current step for non-GC
      technologies.

### 2.2.3. Control API

This API can be used only on Root AsyncSteps objects.

1. `void execute()` - must be called only once after the root object steps are
   configured.
    * Initiates AsyncSteps execution implementation-defined way using the
      associated instance of AsyncTool.
1. `void cancel()` - may be called on the root object to asynchronously cancel
   execution.
    * Cancellation typically happens on continuation of `AsyncSteps` execution.
    * Inner-cancel must be done with `asi.error()`.
1. `Promise promise()` - must be called only once after the root object steps
   are configured.
    * Wraps `execute()` into a native Promise object.
    * Returns a native Promise or Future object.

### 2.2.4. Execution Loop API

This API can be used only inside `execute_callback`.

1. `void loop( func, [, label] )`:
    * executes the loop until `asi.break()` is called;
    * `func( asi )` - the loop body;
    * `label` - am optional label to use for `asi.break()` and `asi.continue()`
      in inner loops.
1. `void forEach( map|list, func [, label] )`:
    * for each `map` or `list` element, call `func( asi, key, value )`;
    * `func( asi, key, value )` - the loop body;
    * `label` - an optional label to use for `asi.break()` and `asi.continue()`
      in inner loops.
1. `void repeat( count, func [, label] )`:
    * calls `func(asi, i)` for `count` times;
    * `count` - how many times to call the `func`;
    * `func( asi, i )` - the loop body, `i` - the current iteration starting
      from `0`;
    * `label` - an optional label to use for `asi.break()` and `asi.continue()`
      in inner loops.
1. `void break( [label] )`:
    * breaks execution of the current loop;
    * also raises a special exception which gets handled by `AsyncSteps`
      internally;
    * `label` - unwinds nested loops, until `label` named loop is exited.
    * the label must be recorded as `error_info`.
1. `void continue( [label] )`:
    * continue loop execution from the next iteration;
    * also raises a special exception which gets handled by `AsyncSteps`
      internally;
    * `label` - break nested loops, until `label` named loop is found.
    * the label must be recorded as `error_info`.

### 2.3. `Mutex` class

* It must implement the `ISync` interface.
* Functions:
    * `c-tor(unsigned integer max=1, unsigned integer max_queue=null)`:
        * sets the maximum number of parallel AsyncSteps entering the critical
          section;
        * `max_queue` - optionally, limit the queue length.

### 2.4. `Throttle` class

* It must implement the `ISync` interface.
* Functions:
    * `c-tor(unsigned integer max, unsigned integer period_ms=1000, unsigned integer max_queue=null)`:
        * sets the maximum number of the critical section entries within the
          given time period;
        * `period_ms` - the time period in milliseconds;
        * `max_queue` - optionally, limit the queue length.

### 2.5. `Limiter` class

* It must implement the `ISync` interface.
* Functions:
    * `c-tor(options)`:
        * Complex limit handling;
        * `options.concurrent=1` - the number maximum of concurrent flows;
        * `options.max_queue=0` - the number maximum of queued flows;
        * `options.rate=1` - the number maximum of the critical section entries
          in the given period;
        * `options.period_ms=1000` - the time period in milliseconds;
        * `options.burst=0` - the number maximum of queued flows for rate
          limiting.

### 2.6. AsyncTool event loop interface

There is a strong assumption that AsyncSteps instances are executed in partial
order by a common instance of event loop, with a historical name AsyncTool.

There is an assumption that AsyncTool will be extended with Input/Output event
support to act as a true reactor, but it may not be always possible.

AsyncTool was not defined in previous versions of the specification because its
interface is specific to technology while it was always existing. Below is only
**a general suggestion**.

1. `Handle immediate( func )`:
    - schedule an immediate callback;
    - `func()` - general callback.
1. `Handle deferred( delay, func )`:
    - schedule a callback with delay;
    - `delay` - typically time period in milliseconds;
    - `func()` - general callback.
1. `bool is_same_thread()`:
    - check if the current operating system thread is the same as the internal
      event loop's one;
    - if applicable at all.
1. `void cancel( handle )`:
    - cancel the previously scheduled callback;
    - it should not be an error, if callback has been already executed;
    - this method may be a part of the `Handle` object's interface.
1. `bool is_valid( handle )`:
    - an ability to check if the handle still refers to scheduled task;
    - this method may be a part of the `Handle` object's interface.

### 2.7. Universal Binary Interface

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

#### 2.7.1. Binary Data

Binary data interface is used to pass `execute_callback` arguments between technologies. Directly
are supported:

1. all ISO C primitive integers, floating point and boolean types,
1. single dimension dynamic arrays(vectors) of such types,
1. 8-, 16- and 32-bit Unicode strings,
1. custom technology-specific types.

For efficiency reasons, complex types like vectors may be stored both in agnostic C format and
as a technology-specific object instance. Therefore, binary value holding object supports
cleanup callbacks to properly destroy such objects even from C or Assembly code.

```c
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

#### 2.7.2. Binary AsyncSteps Interface

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

#### 2.7.3. Binary Synchronization Primitive's Interface

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

## 3.1. Single-Level Steps

    AsyncStepsImpl asi;

    asi.add(
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

## 3.2. Sub-Steps

    AsyncStepsImpl asi;

    asi.add(
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
    
## 3.3. The `parallel()` Steps and `state()`

    AsyncStepsImpl asi;

    asi.add(
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
                inner_as.state().parallel_1,
                inner_as.state().parallel_2
            );
        },
    )
    
## 3.4. Loops

    AsyncStepsImpl asi;
    
    asi.add(
        function( asi ){
            asi.repeat( 3, function( asi, i ) {
                print i;
            } );
            
            asi.forEach( [ 1, 3, 3 ], function( asi, k, v ) {
                print k "=" v;
            } );
            
            asi.forEach( asi.state(), function( asi, k, v ) {
                print k "=" v;
            } );
        },
    )
    
## 3.5. External Event Wait

    AsyncStepsImpl asi;
    
    asi.add(
        function( asi ){
            asi.waitExternal();
            
            callSomeExternal( function(err) {
                if (err)
                {
                    try {
                        asi.error(err);
                    } catch {
                        // ignore
                    }
                }
                else
                {
                    asi.success();
                }
            } );
        },
    )
    
## 3.6. Synchronization

    AsyncStepsImpl asi;
    MutexImpl mutex(10);
    
    asi.sync(
        mutex,
        function( asi ){
            // critical section with regular AsyncSteps
        },
    )
        
    
=END OF SPEC=
