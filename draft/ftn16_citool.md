<pre>
FTN16: FutoIn - Continuous Integration Tool
Version: 1.0
Date: 2017-02-23
Copyright: 2015-2017 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2017-02-23
* Initial draft - 2015-09-14


# 1. Intro

There are many continuous integration tools, but they are primarily targeted at own
infrastructure. The demand for a new tool is to merge many different technologies
like npm, composer, bundle, bower and others under a single tool for project development,
build, deployment and running.

*NOTE: current focus is on web projects, but support of other types is a far target.*

# 2. Concept

A command line tool must be available through shell search path or called via absolute path.
The command name is "citool" - Continuous Integration Tool.

"citool" must work on existing projects with no modifications, but with extra parameters required.
If special "futoin.json" configuration file is present in project root then extra parameters'
default values should be taken from the configuration file.

It should be possible to specify any of the actions manually through configuration file. Otherwise,
the tool should auto-detect action implementation.

The tool should support the following actions:
* tag
* prepare
* build
* package
* promote
* deploy
* vcs_deploy
* run
* ci_build
* tool

## 2.1. Tag

A standard procedure for updating for release and tagging source code.

## 2.2. Preparation

A standard procedure for project development or release is source checkout, dependency checkout
and workspace configuration.

## 2.3. Building

A standard procedure for detecting available build systems and executing them in predefined order.
Binary artifact may be a product of such action.

## 2.4. Packaging

A standard procedure for detecting packaging method to create a single
binary artifact for deployment.

## 2.5. Promotion

A standard procedure for promoting a binary package into predefined release
management chains:

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

## 2.6. Deployment

The primary focus of the action is for setup of web projects. The process should
properly check requirements, setup file permissions, manage persistent data,
manage configuration and support rolling deployment with no service interruption.

## 2.7. Running

This action should focused on service execution in development process and
may not be implemented at all, if not applicable.

# 3. Detailed business logic definition

## 3.1. Configuration file

Name: futoin.json
Format: strict JSON
Location (project): project root folder
Process environment: (only whitelisted variables for .env part)
Location (deployment): ${DEPLOY_ROOT} (only .env part)
Location (user): ${HOME}/.futoin.json (only .env part)
Location (global): /etc/futoin.json (only .env part)

### 3.1.1. JSON tree definition in dot notation.

The same identifiers should be used in command line options. All configuration nodes are optional
and auto-detectable in most cases.

* .name - project's full unique name
* .version - project's version
* .target - (dynamic variable) current build target
* .vcsRepo - source repository
* .vcs - version control system type:
    * "svn"
    * "git"
    * "hg"
* .vcsRef - (dynamic variable) current branch name
* .wcDir - (dynamic variable) working directory name for fresh clone/checkout
* .deployDir - (dynamic variable) root for current package deployment
* .reDeploy - (dynamic variable) force deploy, if true
* .rmsRepo - binary artifact Release Management System location
* .rmsPool - sub-path/pool in .rmsRepo
* .rms - release management system type:
    * "svn" - use Subversion as binary artifact repository
    * "scp" - use SSHv2 FTP
    * "archiva" - use Apache Archiva
    * "artifactory" - use JFrog Artifactory
    * "nexus" - use Sonatype Nexus
* .tools - {}, list of required tool=>version pairs with possible standard keys:
    * 'nvm'
    * 'rvm'
    * 'php'
    * 'python'
    * 'node'
    * 'ruby'
    * 'composer'
    * 'npm'
    * 'grunt'
    * 'gulp'
    * 'bower'
    * 'puppet'
* .tool - (dynamic variable) current tool to be used
* .package - [], content of package relative to project root. Default: [ "." ]
* .persistent - [], list of persistent read-write directory paths.
    The paths must be empty/missing in deployment package.
* .main - {], list of named entry points {}
    * .type - "php", "node", "python" and "php-cli" (auto-detect by default)
    * .path - file (not required in some cases, e.g. php-fpm)
    * .tune - {}, type-specific configuration options
* .configenv - {} - list of environment variables to be set in deployment
    * type - FutoIn variable type
    * desc - variable description
* .webcfg - additional web server configuration
    * .root - web root folder relative to project root
    * .index - default index handler from .main
    * .nginx - path to nginx vhost config include relative to project root
    * .apache - path to apache vhost config include relative to project root
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
    * .run - custom shell command to run after deployment
    * .runDev - custom shell command to run from source
* .env - {}, the only part allowed to be defined in user or system configs
    * .type - "prod", "uat", "qa" and "dev" (default - "dev")
    * .startup - "cron", "systemd" (default - "cron")
    * .webServer:
        * "nginx"
        * "apache" - not supported yet
    * .mainConfig: {}
        * .main-specific deployment configurations
    * .persistentDir = {.deployDir}/persistent - root for persistent data
    * .vars - arbitrary environment variables to set on execution
    * .plugins = {} - custom plugins $tool:$module_name pairs
    * .{tool}Bin - path to "$tool" command line binary
    * .{tool}Dir - path root "$tool", if applicable
    * .{tool}Ver - required version of "$tool", if applicable
    * .{tool}{misc} - any tool-specific misc. configuration
    * .externalSetup - {}, custom external setup hooks
        * .runCmd - command to execute instead of standard "run"
        * .webServer = false - skip web server setup, if true
        * .startup = false - skip startup scripts, if true
        * .installTools = false - skip automatic tools install, if true

### 3.1.2. Process environment

Each tool may have a whitelist of related environment variables for .env sections.
This variables may be passed through process environment as well. Example:

```bash
    rubyVer=2.3.3 citool tool install ruby
```

## 3.2. Commands

Prior to each command run:

* Read user and system locations for .env configuration
* Setup .env.vars
* Read project's futoin.json, if present
* For each composer.json, package.json, bower.json (in strict order):
    * set .name, if not set yet
    * set .version, if not set yet
    * set .vcsRepo, if not set yet
    * set .rmsRepo, if not set yet
* if .name is set (run in project root):
    * If .tools is not set yet, configure based on file presence in project root:
        * composer.json -> composer, php
        * package.json -> npm, node
        * bower.json -> bower, node
        * Gruntfile.js, Gruntfile.coffee -> grunt, node
        * gulpfile.js -> gulp, node
        * metadata.json -> puppet
    * For each .tools detect related .env.*Bin, if not set
        * Ask to execute install procedures, if tool is missing
        * Fail, if not interactive prompt (e.g. automatic deployment)
    * Detect .vcs and related .env.*Bin, if not set
    * Detect .vcsRepo, if not set yet
    * Detect current .vcsRef

Standard parameter processing:

* if --vcsRepo is provided
    * set .vcsRepo and .vcs
    * verify we are in the correct working copy
* else auto-detect based on VCS working copy or use .vcsRepo
* if --rmsRepo is provided
    * set .rmsRepo

Standard checkout process:

* if svn: switch or checkout .vcsRef
* otherwise: clone & checkout or fetch & checkout .vcsRef
* re-init configuration



### 3.2.1. citool tag &lt;branch> [&lt;next_version>] [--vcsRepo=&lt;vcs:url>] [--wcDir wc_dir]

Default:

* process standard parameters
* Set .vcsRef={branch}
* standard checkout process
* if --version is set then set .version
* otherwise, increment the very last part of .version
* Update (or create) futoin.json with release version
* Update tool configuration files with release version
* Commit updated files with "Updated for release {.name} {.version}" comment
* Create [annotated] tag "v{.version} with "Release {.name} {.version}" comment
* Push changes and tags, if applicable based on .vcs

### 3.2.2. citool prepare [&lt;vcs_ref>] [--vcsRepo=&lt;vcs:url>] [--wcDir wc_dir]

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

### 3.2.3. citool build

Default:

* depending on .tools:
    * grunt -> {.env.gruntBin}
    * gulp -> {.env.gulpBin}
    * puppet -> {.env.puppetBin} module build

### 3.2.4. citool package

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
* CI build: {.name}-CI-{.version}-{.ref}-{YYYYMMDD_hhmmss}[-{target}].ext
* where:
    * .name & .version - from configuration
    * .ref - revision from VCS
    * target, if no neutral to Arch/OS execution environment
    * all forbidden symbols must get replaced with underscore


### 3.2.5. citool promote &lt;package> &lt;rms_pool> [--rmsRepo=&lt;rms:url>] [--rmsHash=&lt;type:value>]

Default:

* process standard parameters
* if {package} file exists use it
* otherwise, use one from .rmsRepo
* if --rmsHash is given
    * verify {package} against it
* otherwise
    * get/calc {package} hash and prompt for confirmation
* if local package
    * upload {package} to {.rmsrepo}/{pool}
* otherwise
    * RMS-specific promote {package} to {.rmsrepo}/{pool}

### 3.2.6 citool deploy &lt;deploy_type> ...

### 3.2.6.1 citool deploy [rms] &lt;rms_pool> [&lt;package>] [--rmsRepo=&lt;rms:url>] [--redeploy] [--deployDir deploy_dir]

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
* common deploy procedure, package_dir = {package_no_ext}

#### 3.2.6.2. citool deploy vcstag [&lt;vcs_ref>] [--vcsRepo=&lt;vcs:url>] [--redeploy] [--deployDir deploy_dir]

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
* common deploy procedure, package_dir = {vcs_ref}

#### 3.2.6.3. citool deploy vcsref &lt;vcs_ref> [--vcsRepo=&lt;vcs:url>] [--redeploy] [--deployDir deploy_dir]

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
* common deploy procedure, package_dir = {vcs_ref}_{vcs_rev}

#### 3.2.6.3. common deploy procedure

* {package_dir} - depend on deployment method
* according to .persistent:
    * create symlinks {.deployDir}/{package_dir}.tmp/{subpath} -> {.env.persistentDir}/{subpath}
* setup read-only permissions
* run .action.migrate
* setup runtime according to .main config
* setup per-user web server (nginx)
* atomic move {.deployDir}/{package_dir}.tmp {.deployDir}/{package_dir}
* create/change symlink {.deployDir}/current -> {.deployDir}/{package_dir}
* reload web server and runtime according to .main
* remove all not managed or obsolete files in {.deployDir}

#### 3.2.6.4. deployment assumptions

1. Each web application must have own deployment root folder
2. Each web application should have own user
3. Each web application should get proper ownership and read-only permissions
4. Application package must not have modifiable content
5. Each read-write path should get symlink to {.env.persistentDir}/{path} and survive across deployments
6. .action.migrate must run and successfully complete
7. ${.deployDir}/vhost.{.env.webServer}.subconf must be generated including packages-specified extensions
8. Automatic startup must get enabled
9. ${.deployDir}/current must always point to fully configured deployment
10. For security reasons it is not possible to include project-specific config
    for web server running as root user. Also, sensitive data like TLS private
    keys must not be available to application user. Therefore a performance
    penalty of reverse proxy may apply, but large high available deployments should
    have load balancer/reverse proxy any way.
11. Web server configuration may be delegated to external functionality.

### 3.2.7. citool run &lt;command=start>

Default per command:

* start:
    * if deployment environment:
        * start services according to deployment configuration
    * if development environment:
        * start services according to project configuration
* stop:
    * stop all running services (even not configured)
* reload:
    * start not running services
    * reload other running services
    * stop not configured services

### 3.2.8. citool ci_build &lt;vcs_ref> &lt;rms_pool> [--vcsRepo=&lt;vcs:url>] [--rmsRepo=&lt;rms:url>]

Default:

* citool prepare
* citool build
* citool package
* citool promote &lt;package> &lt;rms_pool>

### 3.2.9. citool tool &lt;action> [&lt;tool_name> -- optional args]

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

=END OF SPEC=
