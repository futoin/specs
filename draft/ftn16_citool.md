<pre>
FTN16: FutoIn - Continuous Integration Tool
Version: 0.1
Date: 2015-09-14
Copyright: 2014 FutoIn Project (http://futoin.org)
Authors: Andrey Galkin
</pre>

# CHANGES

* v1.0 - 2015-09-14


# 1. Intro

There are many continuous integration tools, but they are primarily targeted at own
infrastructure. The demand for a new tool is to merge many different technologies
like npm, composer, bundle, bower and others under a single tools for project development,
build, deployment and running.

*NOTE: current focus is on web projects, but support of other types is a far target.*

# 2. Concept

A command line tool must be available through shell search path or called via absolute path.
The command name is "citool" - Continuous Integration Tool.

"citool" must work on existing projects with no modifications, but with extra parameters required.
If special "futoin.json" configuration file is present in project root then extra parameters'
default values should be taken from the configuration file.

It should possible to specify any of the actions manually through configuration file. Otherwise,
the tool should auto-detect action implementation.

The tool should support the following actions:
* tag
* prepare
* build
* package
* promote
* deploy
* run

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

* Build -> CI Builds
* Build -> Release Builds -> Production Builds
* Build -> *{Arbitrary}*
* *{Arbitrary}* -> *{Arbitrary}* [-> *{Arbitrary}*]+

Where:

* Build - binary artifact, product of clean build process
* CI Builds - pool with development builds without source tagging
* Release Builds - pool with builds from source tags
* Production Builds - QA validated and Management approved Release Builds
* *{Arbitrary}* - any custom binary artifact pool

*Note: promotion from pool to pool must not modify binary artifacts. Otherwise,
a separate project must exist, which uses original project binary artifact as
dependency for input and own binary artifact promotion chains*

## 2.6. Deployment

A standard implementation of this action should be implemented only for web projects
with quite specific requirements on target environment. Target environment
may have a global configuration file "/etc/futoin/futoin.json" to override
the default settings.

## 2.7. Running

A standard implementation of project execution depends on the deployment procedure.
The deployment procedure must leave clear artifacts in operating system
service management for proper startup, control and supervision.

### 2.7.1. Execution in Development

A special case when project is run from source build folder during development.
This case must be auto-detected.

# 3. Detailed business logic definition

## 3.1. Configuration file

Name: futoin.json
Format: strict JSON
Location (project): project root folder
Location (user): ${HOME}/.futoin/ (only .env part)
Location (global): /etc/futoin/ (only .env part)

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
* .vcsBranch - (dynamic variable) current branch name
* .rmsRepo - binary artifact Release Management System location
* .rms - release management system type:
    * "svn" - use Subversion as binary artifact repository
    * "sftp" - use SSHv2 FTP
    * "artifactory" - use JFrog Artifactory
    * "nexus" - use Sonatype Nexus
* .tools - [], list of tools supported by the project with possible values:
    * "php"
    * "nodejs"
    * "npm"
    * "bower"
    * "grunt"
    * "gulp"
    * "composer"
* .package - [], content of package relative to project root. Default: [ "." ]
* .writeable - [], list of read-write paths (must be empty/missing in deployment package)
* .main - {], list of named entry points {}
    * .type - "php-fpm", "nodejs", "python" and "php-cli" (auto-detect by default)
    * .path - file (not required in some cases, e.g. php-fpm)
    * .tune - {}, type-specific configuration options
* .configenv - {} - list of environment variables to be set in deployment
    * type - FutoIn variable type
    * desc - variable description
* .webcfg - additional web server configuration
    * .root - web root folder relative to project root
    * .index - default index handler
    * .nginx - path to nginx vhost config include relative to project root
    * .apache - path to apache vhost config include relative to project root
* .actions - {}, optional override of auto-detect commands
    * .tag - custom shell command for tagging
    * .prepare - custom shell command for source preparation
    * .build - custom shell command for building from source
    * .package - custom shell command for binary artifact creation
    * .promote - custom shell command for binary artifact promotion
    * .deploy - custom shell command for deployment from binary artifact
    * .run - custom shell command to run after deployment
    * .runDev - custom shell command to run from source
* .env - {}, the only part allowed to be defined in user or system configs
    * .type - "prod", "uat", "qa" and "dev" (default - "dev")
    * .init - startup script type:
        * "systemd"
        * "sysv"
        * "cron" - user's cron
    * .webServer:
        * "nginx"
        * "apache"
    * .webConfigDir - root directory for virtual host configuration,
        default:  "/etc/{.env.webServer}/sites-enabled"
    * .createUsers=false - auto create users on deployment
    * .vars - arbitrary environment variables to set on execution
    * .phpBin - path to "php" command line tool
    * .pythonBin - path to "python" command line tool
    * .nodejsBin - path to "nodejs" command line tool
    * .svnBin - path to "svn" command line tool
    * .gitBin - path to "git" command line tool
    * .hgBin - path to "hg" command line tool
    * .composerBin - path to "composer" command line tool
    * .npmBin - path to "npm" command line tool
    * .gruntBin - path to "grunt" command line tool
    * .gulpBin - path to "gulp" command line tool


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
        * package.json -> npm, nodejs
        * bower.json -> bower, nodejs
        * Gruntfile.js, Gruntfile.coffee -> grunt, nodejs
        * gulpfile.js -> gulp, nodejs
    * For each .tools detect related .env.*Bin, if not set
        * Execute install procedures, if tool is missing
    * Detect .vcs and related .env.*Bin, if not set
    * Detect .vcsRepo, if not set yet
    * Detect current .vcsBranch

Standard parameter processing:

* if --vcsRepo is provided
    * set .vcsRepo and .vcs
    * verify we are in the correct working copy
* else auto-detect based on VCS working copy or use .vcsRepo
* if --rmsRepo is provided
    * set .rmsRepo

Standard checkout process:

* if svn: switch or checkout .vcsBranch
* otherwise: clone & checkout or fetch & checkout .vcsBranch
* re-init configuration



### 3.2.1. citool tag {branch} [--version=next_increment] [--vcsRepo=from futoin.json]

Default:

* process standard parameters
* Set .vcsBranch={branch}
* standard checkout process
* if --version is set then set .version
* otherwise, increment the very last part of .version
* Update (or create) futoin.json with release version
* Update tool configuration files with release version
* Commit updated files with "Updated for release {.name} {.version}" comment
* Create [annotated] tag "v{.version} with "Release {.name} {.version}" comment
* Push changes and tags, if applicable based on .vcs

### 3.2.2. citool prepare [--ref=working copy, master or trunk] [--vcsRepo=from futoin.json]

Default:

* process standard parameters
* if --ref is supplied then set .vcsBranch and make standard checkout process
* depending on .vcs and .tools:
    * svn -> {.env.svnBin} update
    * git -> {.env.gitBin} pull --rebase [&& {.env.gitBin} submodule update]
    * hg -> {.env.hgBin} pull --update
    * composer -> {.env.composerBin} install
    * npm -> {.env.npmBin} install

### 3.2.3. citool build

Default:

* depending on .tools:
    * grunt -> {.env.gruntBin}
    * gulp -> {.env.gulpBin}

### 3.2.4. citool package

Default:

* if package is product of the build process then exit
* for each .tools
    * remove related external dependencies for development
* create .tar.xz package based .package list

#### 3.2.3.1. Package name convention:

* Release build: {.name}-{.version}-{YYYY-MM-DD}[-{target}].ext
* CI build: {.name}-CI-{.version}-{.ref}-{YYYY-MM-DD}[-{target}].ext
* where:
    * .name & .version - from configuration
    * .ref - revision from VCS
    * target, if no neutral to Arch/OS execution environment
    * all forbidden symbols must get replaced with underscore


### 3.2.5. citool promote {package} {pool} [--rmsRepo=from futoin.json] [--hash={TYPE:value}]

Default:

* process standard parameters
* if {package} file exists use it
* otherwise, use one from .rmsRepo
* if --hash is given
    * verify {package} against it
* otherwise
    * get/calc {package} hash and prompt for confirmation
* if local package
    * upload {package} to {.rmsrepo}/{pool}
* otherwise
    * RMS-specific promote {package} to {.rmsrepo}/{pool}

### 3.2.6. citool deploy {package} {location=[deployuser:]runuser@host} [--rmsRepo=from futoin.json] [--hash={TYPE:value}]

Default:

* process standard parameters
* if {package} file exists use it
* otherwise, use one from .rmsRepo
* if --hash is given
    * verify {package} against it
* otherwise
    * get/calc {package} hash and prompt for confirmation
* parse {location}, deployuser=runuser by default
* retrieve {package} from RMS
* upload {package} and generated {package}.sh to deployuser@host:/tmp
* execute remote deployuser@host:/tmp/{package}.sh

#### 3.2.5.1. {package}.sh deployment script generation assumptions

1. Each web application should have own user
2. Each user should have home folder 
3. Each {package} should get unpacked to ${HOME}/{package}
4. Each ${HOME}/{package} should get proper ownership and read-only permissions
5. Each read-write path should get symlink to ${HOME}/persistent/{path} and survive across deployments
6. Pre-deployment must run and successfully complete
7. ${HOME}/vhost.{.env.webServer} must be generated including packages-specified extensions
8. Automatic startup must get enabled
9. ${HOME}/current symlink must get changed to ${HOME}/{package}
10. Web server and related daemons must get reloaded

#### 3.2.7. citool run {package}

Default:

* if deployment environment:
    * start services according to configuration
* if development environment:
    * start services and webserver
    * make them available on the first available port starting from localhost:8080

=END OF SPEC=
