<pre>
FTN16: FutoIn - Continuous Integration & Delivery Tool
Version: 1.0
Date: 2017-04-29
Copyright: 2015-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2017-04-29
* Initial draft - 2015-09-14


# 1. Intro

There are many continuous integration & delivery tools, but they are primarily targeted at own
infrastructure. The demand for a new meta-tool is to merge many operations of different
technologies like npm, composer, bundle, nvm, rvm, php-build and others under a single tool for
runtime setup, project development, build, deployment and running.

*NOTE: current primary focus is on web projects, but other cases like Puppet modules are supported.*

# 2. Concept

A command line tool must be available through shell search path or called via absolute path.
The command name is "cid" - Continuous Integration & Delivery Tool.

"cid" must work on existing projects with no modifications, but with extra parameters required.
If special "futoin.json" configuration file is present in project root then extra parameters'
default values should be taken from the configuration file.

It should be possible to specify any of the actions manually through configuration file. Otherwise,
the tool should auto-detect action implementation.

The tool should support the following actions:

* tag
* prepare
* build
* package
* check
* promote
* deploy
* run
* ci_build
* tool
* init
* migrate
* vcs
* rms
* service

## 2.1. Tag

A standard procedure for updating for release and tagging source code.

## 2.2. Preparation

A standard procedure for project development or release is source checkout, dependency checkout
and workspace configuration.

For build tools, working copy clean up is expected.

## 2.3. Building

A standard procedure for detecting available build systems and executing them in predefined order.
Binary artifact may be a product of such action.

## 2.4. Checking

A standard procedure for detecting available test systems and executing them in predefined order.

## 2.5. Packaging

A standard procedure for detecting packaging method to create a single
binary artifact for deployment.

## 2.6. Promotion

A standard procedure for promoting a binary package into predefined release
management systems (RMS).

Suggested name conventions:
* Build -> CIBuilds
* Build -> ReleaseBuilds -> ProductionBuilds
* Build -> *{Arbitrary}*
* *{Arbitrary}* -> *{Arbitrary}* [-> *{Arbitrary}*]+

Where:

* Build - binary artifact, product of clean build process
* CIBuilds - RMS pool with development builds without source tagging
* ReleaseBuilds - RMS pool with builds from source tags
* ProductionBuilds - QA validated and Management approved Release Builds
* *{Arbitrary}* - any custom binary artifact pool

*Note: promotion from pool to pool must not modify binary artifacts. Otherwise,
a separate project must exist, which uses original project binary artifact as
dependency for input and own binary artifact promotion chains*

## 2.7. Deployment

The primary focus of the action is for setup of web projects. The process should
properly check requirements, setup file permissions, manage persistent data,
manage configuration and support rolling deployment with no service interruption.

## 2.8. Running

This action should focused on execution in development and testing process and
may not be implemented at all, if not applicable.

# 3. Detailed business logic definition

## 3.1. Configuration file

* Name: futoin.json
* Format: strict JSON
* Location (project): project root folder (without .env part)
* Process environment: (only whitelisted variables for .env part)
* Location (deployment): ${DEPLOY_ROOT} (both config options and .env part)
* Location (user): ${HOME}/.futoin.json (only .env part)
* Location (global): /etc/futoin.json (only .env part)

### 3.1.1. JSON tree definition in dot notation.

The same identifiers should be used in command line options. All configuration nodes are optional
and auto-detectable in most cases.

*Note: this tree represents actual state CID works with. All internal API either work with full
configuration root or only with its .env part. There should be no other configuration data.*

#### 3.1.1.1. Project configuration

* .name - project's full unique name
* .version - project's version
* .vcsRepo - source repository
* .vcs - version control system type:
    * "svn"
    * "git"
    * "hg"
* .deployBuild - force build on deploy, if true
* .permissiveChecks - allows check failure, if true
* .rmsRepo - binary artifact Release Management System location
* .rmsPool - sub-path/pool in .rmsRepo
* .rms - release management system type:
    * "svn" - use Subversion as binary artifact repository
    * "scp" - use SSHv2 FTP
    * "archiva" - use Apache Archiva
    * "artifactory" - use JFrog Artifactory
    * "nexus" - use Sonatype Nexus
* .tools - {}, map of required tool=>version pairs.
    Default version is marked as `true` or `'*'`.
    Tool name is all lower case letters with optional digits (except the first position).
* .toolTune - {}, map of maps tool=>settings=>value for fine tuning of tool behavior
* .package - [], content of package relative to project root. Default: [ "." ]
* .packageGzipStatic = True, creates *.gz files for found *.js, *.json, *.css, *.svg and *.txt files
* .packageChecksums = True, creates .package.checksums of files
* .persistent - [], list of persistent read-write directory paths.
    The paths must be empty/missing in deployment package.
* .entryPoints - {], list of named entry points {}
    * .tool - name of the tool
    * .path - file
    * .tune - {}, type-specific configuration options (extandable)
        * .minMemory - minimal memory per instance
        * .connMemory - memory per one connection
        * .scalable = true - if false then it's not allowed to start more than one instance globally
        * .reloadable = false -if true then reload is supported
        * .cpuWeight = 100 - arbitrary positive integer
        * .memWeight = 100 - arbitrary positive integer
        * .maxMemory - maximal memory per instance (for very specific cases)
        * .maxInstances - limit number of instances per deployment
        * .socketTypes = ['unix', 'tcp', 'tcp6'] - supported listen socket types
        * .socketProtocols = ['http', 'fcgi', 'wsgi', 'rack', 'jsgi', 'psgi']
        * .debugOverhead - extra memory per instance in "dev" deployment
        * .debugConnOverhead - extra memory per connection in "dev" deployment
* .configenv - {} - list of environment variables to be set in deployment
    * type - FutoIn variable type
    * desc - variable description
* .webcfg - additional web server configuration (auto-requires web server)
    * .root - web root folder relative to project root
    * .main - default index handler from .entryPoints (auto-select, if single one)
* .actions - {}, optional override of auto-detect commands.
    Each either a string or list of strings. Use '&lt;default>' in [] to run the
    default auto-detected tasks too.
    * .tag - custom shell command for tagging
    * .prepare - custom shell command for source preparation
    * .build - custom shell command for building from source
    * .package - custom shell command for binary artifact creation
    * .promote - custom shell command for binary artifact promotion
    * .migrate - custom shell command in deployment procedure
    * .deploy - custom shell command for deployment from binary artifact
    * .{custom} - any arbitrary user-defined extension to use with "cid run"
* .plugins = {} - optional custom plugins, see .env counterpart
* .pluginPacks = [] - optional custom plugin packs, see .env counterpart

#### 3.1.1.2. Environment configuration

* .env - {}, the only part allowed to be defined in user or system configs
    * .type - "prod", "test" and "dev" (default - "dev")
    * .persistentDir = {.deployDir}/persistent - root for persistent data
    * .vars - arbitrary environment variables to set on execution
    * .plugins = {} - custom plugins, implementation defined
        * $tool => $module_name pair - individual tool
    * .pluginPacks = [] - custom plugin packs, implementation defined
        * $module_name - define module providing list of plugins
    * .binDir = ${HOME}/bin - user bin folder
    * .externalSetup - false - skip automatic tools install, if true
    * .timeouts - timeout configuration for various operations (may not be always supported)
        * .connect = 10 - initial connection timeout 
        * .read = 60 - network timeout for individual read calls
        * .total = .read * 60 - network timeout for single request
    * .{tool}Bin - path to "$tool" command line binary
    * .{tool}Dir - path root "$tool", if applicable
    * .{tool}Ver - required version of "$tool", if applicable
    * .{tool}{misc} - any tool-specific misc. configuration

#### 3.1.1.3. Deployment configuration

* .deploy
    * .maxTotalMemory - memory limit for deployment
    * .maxCpuCount - CPU count the deployment expected to utilize
    * .autoServices - {}, to be auto-generated in deployment process
        * .maxMemory - maximal memory per instance (for deployment config)
        * .maxClients - expected number of clients the instance can handle
        * .socketType - one of .entryPoints[.entryPoint].socketTypes
        * .socketAddr - assigned socket address, if applicable
        * .socketPort - assigned socket port, if applicable
        * .socketPath - assigned socket path, if applicable

#### 3.1.1.4. Runtime configuration (available to plugins)

* .target - (dynamic variable) current build target
* .vcsRef - (dynamic variable) current branch name
* .wcDir - (dynamic variable) working directory name for fresh clone/checkout
* .deployDir - (dynamic variable) root for current package deployment
* .reDeploy - (dynamic variable) force deploy, if true
* .debugBuild - (dynamic variable) build in debug mode
* .tool - (dynamic variable) current tool to be used
* .toolVer - (dynamic variable) required version for current tool
* .toolOrder - (dynamic variable) full ordered by dependency list of active tools
* .packageFiles - (dynamic variable), list of packages created by tools

#### 3.1.1.5. Python-based CID implementation notes

1. `.plugins` expects to fully qualified module named with `{tool}Tool` class.
2. `.pluginPacks` expect fully qualified module name with submodules
    in `{tool}tool.py` format having `{tool}Tool` class

### 3.1.2. Process environment

Each tool may have a whitelist of related environment variables for .env sections.
This variables may be passed through process environment as well. Example:

```bash
    rubyVer=2.3 cid tool install ruby
    rubyVer=2.3 cid tool exec ruby -- ruby-specific-args
```

### 3.1.3. Working Directory notes

By default working directory (--wcDir) is absolute path of current working directory, except:

1. If ci_build command is used with --vcsRepo then absolute path of "./ci_build_{vcs_ref}" is used
2. If ci_build command is used without --wcsRepo then:
    * project name is taken as basename of current working directory
    * working directory is set to absolute path of "../ci_builds/{project_name}_{vcs_ref}"

In all cases working directory must be either empty or contain project without conflicts 
with --vcsRepo parameter, if supplied.

In case of ci_build, it is required to make a clean checkout. Therefore, existing wcDir
must be removed (renamed for safety).


#### 3.1.4. Resource distribution requirements

The complexity comes from these facts:

* Some runtimes are single-threaded with async IO.
    * does not scale beyond one CPU - requires multiple instances
    * multiple instances - lead to multiple sockets
* Some apps are not scalable to multiple instances and lack High-Availability.
* Some runtimes have thread/process per client with single control socket.
* Some runtimes support seamless reload.
* Actual use cases, may require different strategy. Therefore, the specification 
    does not define a strict algorithm, but adds requirements for it.

Requirements:

1. Minimal and maximal memory requirements per service instance must be obeyed.
2. Deployment must fail, if minimal memory requirements are not satisfied.
3. All available for deployment memory must be allocated to instances based
    their weights.
4. If one instance is unable to utilize multiple CPU cores then additional
    instances must be added until it's feasible to distribute available memory.
5. If one instance is unable to seamlessly reload then at least one more
    instance must be added for rolling updates.
6. If app is marked as not scalable then no more than one instance is allowed.

    
## 3.2. Commands

Prior to each command run:

* Read user and system locations for .env configuration
* Setup .env.vars
* Read project's futoin.json, if present
* If .tools is not set yet, configure based on file presence in project root
* For each detected tool, read its configuration:
    * set .name, if not set yet
    * set .version, if not set yet
    * set .vcs and .vcsRepo, if not set yet
    * set .rms and .rmsRepo, if not set yet

Standard parameter processing:

* if --vcsRepo is provided
    * set .vcs and .vcsRepo
    * verify we are in the correct working copy
* else auto-detect based on VCS working copy or use .vcsRepo
* if --rmsRepo is provided
    * set .rms and .rmsRepo


### 3.2.1. cid tag &lt;branch> [&lt;next_version>] [--vcsRepo=&lt;vcs:url>] [--wcDir wc_dir]

Default:

* process standard parameters
* Set .vcsRef={branch}
* standard checkout process
* if &lt;next_version> is set then
    * if equal to 'major', 'minor' or 'patch' then use special logic
        * patch: x.y.z -> x.y.(z+1)
        * minor: x.y.z -> x.(y+1).0
        * major: x.y.z -> (x+1).0.0
    * otherwise check valid version & set .version
* otherwise, increment the very last part of .version
* Update (or create) futoin.json with release version
* Update tool configuration files with release version
* Commit updated files with "Updated for release {.name} {.version}" comment
* Create [annotated] tag "v{.version} with "Release {.name} {.version}" comment
* Push changes and tags, if applicable based on .vcs

#### Versioning notes

It is required that version consists of three components: major, minor and patch.
Generally, [SEMVER](http://semver.org/) is assumed.

### 3.2.2. cid prepare [&lt;vcs_ref>] [--vcsRepo=&lt;vcs:url>] [--wcDir wc_dir]

Default:

* process standard parameters
* if vcs_ref is supplied then set .vcsRef and make standard checkout process
* depending on .vcs and .tools:
    * svn -> {.env.svnBin} update
    * git -> {.env.gitBin} pull --rebase [&& {.env.gitBin} submodule update]
    * hg -> {.env.hgBin} pull --update
    * composer -> {.env.composerBin} install
    * npm -> {.env.npmBin} install
    * bower -> {.env.bowerBin} install
    * etc.

### 3.2.3. cid build [--debug]

Default:

* depending on .tools:
    * grunt -> {.env.gruntBin}
    * gulp -> {.env.gulpBin}
    * puppet -> {.env.puppetBin} module build
    * etc.

### 3.2.4. cid package

Default:

* if package is product of the build process then exit
* for each .tools
    * remove related external dependencies for development
* if .webcfg.root
    * create nginx optimized *.gz files for static content (.js, .json, .css, .svg)
* create sorted sha256 checksums file based on .package list
* create .tar.xz package based on .package list and include the checksums file

#### 3.2.3.1. Package name convention:

* Release build: {.name}-{.version}-{YYYYMMDD_hhmmss}[-{target}].ext
* CI build: {.name}-CI-{.version}-{YYYYMMDD_hhmmss}-{.ref}[-{target}].ext
* where:
    * .name & .version - from configuration
    * .ref - revision from VCS
    * target, if no neutral to Arch/OS execution environment
    * all forbidden symbols must get replaced with underscore

### 3.2.5. cid check [--permissive]

* depending on .tools:
    * run code checks, unit tests, static analysis & misc.
* allow failures, if --permissive

### 3.2.6. cid promote &lt;rms_pool> &lt;packages> [--rmsRepo=&lt;rms:url>]

Default:

* process standard parameters
* if `rms_pool` has colon (':')
    * act as promotion between pools
    * split `rms_pool` into `src_pool` and `dst_pool`
    * for each `package` in `packages`:
        * format: "base_name[@hash_type:hash]"
        * if `package` contains "@"
            * verify the hash in `src_pool`
        * copy package from `src_pool` to `dst_pool` the most efficient way
* else:
    * act as file upload
    * for each `package` in `packages`:
        * upload local `package` into `rms_pool`

### 3.2.7 cid deploy &lt;deploy_type> ...

Generic options:

* [--redeploy] - force re-deploy
* [--deployDir=&lt;deploy_dir>] - target deployment folder
* [--limit-memory=&lt;mem_limit>] - limit memory
* [--limit-cpus=&lt;cpu_count>] - limit CPU count


### 3.2.7.1 cid deploy [rms] &lt;rms_pool> [&lt;package>] [--rmsRepo=&lt;rms:url>] [--build]

Default:

* process standard parameters
* find out the latest package:
    * get list of packages from RMS pool, use package as glob hint
    * filter package list using "package" as glob filter
    * naturally sort package list
    * select the latest
* find out currently deployed package
* if current matches target package and --redeploy is not set then exit
* if {package} file exists then use it
* otherwise, download one from .rmsRepo
* unpack package to {.deployDir}/{package_no_ext}.tmp
* if --build then prepare & build
* common deploy procedure, package_dir = {package_no_ext}

#### 3.2.7.2. cid deploy vcstag [&lt;vcs_ref>] [--vcsRepo=&lt;vcs:url>]

Default:

* process standard parameters
* find out the latest tag:
    * get list of packages from RMS pool, use vcs_ref as glob hint
    * filter tags list using vcs_ref as glob filter
    * naturally sort tag list
    * select the latest
* if {.deployDir}/vcs exists:
    * reset all change
    * fetch/update to vcs_ref
* otherwise:
    * fresh clone/checkout vcs_ref
* find out currently deployed tag
* if current matches target tag and --redeploy is not set then exit
* export vcs_ref to {.deployDir}/{vcs_ref}.tmp
* prepare & build
* common deploy procedure, package_dir = {vcs_ref}

#### 3.2.7.3. cid deploy vcsref &lt;vcs_ref> [--vcsRepo=&lt;vcs:url>]

Default:

* process standard parameters
* if {.deployDir}/vcs exists:
    * reset all change
    * fetch/update to vcs_ref
* otherwise:
    * fresh clone/checkout vcs_ref
* find out the latest revision of vcs_ref as vcs_rev
* find out currently deployed vcs_ref and vcs_rev
* if current matches target and --redeploy is not set then exit
* export vcs_ref to {.deployDir}/{vcs_ref}_{vcs_rev}.tmp
* prepare & build
* common deploy procedure, package_dir = {vcs_ref}_{vcs_rev}

#### 3.2.7.4. common deploy procedure

* {package_dir} - depend on deployment method
* according to .persistent:
    * create symlinks {.deployDir}/{package_dir}.tmp/{subpath} -> {.env.persistentDir}/{subpath}
* setup read-only permissions
* run .action.migrate
* create/update deployment futoin.json
* atomic move {.deployDir}/{package_dir}.tmp {.deployDir}/{package_dir}
* create/change symlink {.deployDir}/current -> {.deployDir}/{package_dir}
* trigger external service reload
* remove all not managed or obsolete files in {.deployDir}

#### 3.2.7.5. deployment assumptions

1. Each web application must have own deployment root folder
2. Each web application should have own user
3. Each web application should get proper ownership and read-only permissions
4. Application package must not have modifiable content
5. Each read-write path should get symlink to {.env.persistentDir}/{path} and survive across deployments
6. .action.migrate must run and successfully complete
7. ${.deployDir}/current must always point to fully configured deployment
8. For security reasons it is not possible to include project-specific config
    for web server running as root user. Also, sensitive data like TLS private
    keys must not be available to application user. Therefore a performance
    penalty of reverse proxy may apply, but large high available deployments should
    have load balancer/reverse proxy any way.
9. Lock file must be acquired during deployment procedure.
10. Not empty {.deploDir} must contain deploy lock file for safety reasons.

### 3.2.8. cid run [&lt;command> [-- &lt;command_args..>]] [--wcDir wc_dir]

Primary case is execution in development and testing environment.

* If command is missing then execute all .entryPoints in parallel
    * Use single instance per entry point
    * Use default memory limits
* Else if command is present in .entryPoints then execute as related tool
* Else if command is present in .actions then execute that in shell

### 3.2.9. cid ci_build &lt;vcs_ref> [&lt;rms_pool>] [--vcsRepo=&lt;vcs:url>] [--rmsRepo=&lt;rms:url>]  [--permissive] [--debug] [--wcDir wc_dir]

Default:

* cid prepare
* cid build
* cid package
* if &lt;rms_pool> is set
    * cid promote {package(s)} &lt;rms_pool>

### 3.2.10. cid tool &lt;action> [&lt;tool_name> [&lt;version>] -- optional args]

Tools actions:

* *exec* -  execute specified tool with arbitrary arguments passed.
* *install* - make sure project tools are installed.
* *install* with tool_name - make sure specified tool is installed even if not used by current project.
* *uninstall* - make sure project tools are uninstalled.
* *uninstall* with tool_name - make sure specified tool is uninstalled
* *update* - make sure the latest versions of tools are used for current project.
* *update* with tool_name - make sure specified tool is installed of the latest version.
* *test* - test if required by current project tools are installed
* *test* with tool_name - check if tool is installed
* *env* - get environment variables after processing of current project tools
* *env* with tool name - get environment variables for specified tool
* *prepare* with tool name - run tool prepare procedure
* *build* with tool name - run tool's build procedure
* *check* with tool name - run tool's check procedure
* *package* with tool name - run tool's package procedure
* *migrate* with tool name - run tool's migrate procedure
* *describe* with tool name - show tool's description
* *list* - list supported tools
* *detect* - list tools detected for current project (with optional "=version")

### 3.2.11. cid init [&lt;project_name>] [--vcsRepo=&lt;vcs:url>] [--rmsRepo=&lt;rms:url>] [--permissive]

Initialize futoin.json. Automatically add already known information to it.

If project name is not provided and not auto-detected then use working copy folder basename.

### 3.2.12. cid migrate

Runs data migration tasks.

Provided for overriding default procedures in scope of deployment procedure.

### 3.2.13. cid vcs &lt;action> [optional args]

These are helpers for CI environment and should not be used by developer in regular activities.

* *cid vcs checkout &lt;vcs_ref> [--vcsRepo=&lt;vcs:url>] [--wcDir=<wc_dir>]* - checkout specific VCS reference
* *cid vcs commit &lt;commit_msg> [<%lt;files>] [--wcDir=<wc_dir>]* - commit & push all changes [or specific files]
* *cid vcs merge &lt;vcs_ref> [--no-cleanup] [--wcDir=<wc_dir>]* - merge another VCS ref. Abort on conflicts.
* *cid vcs branch &lt;vcs_ref> [--wcDir=<wc_dir>]*  - create new branch from current checkout
* *cid vcs delete &lt;vcs_ref> [--vcsRepo=&lt;vcs:url>] [--cacheDir=<cache_dir>] [--wcDir=<wc_dir>]* - delete branch
* *cid vcs export &lt;vcs_ref> &lt;dst> [--vcsRepo=&lt;vcs:url>] [--cacheDir=<cache_dir>] [--wcDir=<wc_dir>]* - export tag or branch
* *cid vcs tags [&lt;tag_pattern>] [--vcsRepo=&lt;vcs:url>] [--cacheDir=<cache_dir>] [--wcDir=<wc_dir>]* - list tags
* *cid vcs branches [&lt;branch_pattern>] [--vcsRepo=&lt;vcs:url>] [--cacheDir=<cache_dir>] [--wcDir=<wc_dir>]* - list branches
* *cid vcs reset [--wcDir=<wc_dir>]* - revert all local changes, including merge conflicts
* *cid vcs ismerged [--wcDir=<wc_dir>]* - check if branch is merged

### 3.2.14. cid rms &lt;action> [optional args]

This helpers help automate RMS operation neutral way.

* *cid rms list &lt;rms_pool> [<package_pattern>] [--rmsRepo=<rms_repo>]* - list available packages
* *cid rms retrieve &lt;rms_pool> <package>... [--rmsRepo=<rms_repo>]* - retrieve-only specified packages
* *cid rms pool create <rms_pool> [--rmsRepo=<rms_repo>]* - ensure pool exists (may require admin privileges)
* *cid rms pool list [--rmsRepo=<rms_repo>]* - list available pools

### 3.2.15. cid service ...

Interface for Continuous Deployment execution control. It is expected to call this commands
from systemd, sysv-init or other system daemon control functionality.

* *cid service exec &lt;entry_point> <&lt;instance> [--deployDir deploy_dir]* -
    replace CID with foreground execution of pre-configured instance.
* *cid service stop &lt;entry_point> <&lt;instance> <&lt;pid> [--deployDir deploy_dir]* -
    stop previously started instance.
* *cid service reload &lt;entry_point> <&lt;instance> <&lt;pid> [--deployDir deploy_dir]* -
    reload previously started instance.

In case containers like Docker is used then there is a separate helper command to be used
as entry point.

* *cid service run [--deployDir deploy_dir]* - run deployment-related services as children and restart on failure.
    * [--adapt] - adapt to newly set limits before execution of services
    * [--limit-memory=&lt;mem_limit>] - limit memory, only with --adapt
    * [--limit-cpus=&lt;cpu_countt>] - limit CPU count, only with --adapt

=END OF SPEC=
