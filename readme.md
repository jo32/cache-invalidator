# Introduction

This little tools accompanied with nginx is used to invalidate browser cache when deploying new version of you site.

# Prerequisite

- nginx, or whatever else can do route redirection

# How It Works

## What Nginx Do

By configurating nginx with:

    if ($query_string ~* "v=([\da-z]+)$") {
        set $v $1;
        rewrite ^/(.*)\.(.*)$ /$1.$2/$v.$2? permanent;
    }

You are able to redirect a request 

	http://YOUR.DOMAIN/route/to/static/file.js?v=versi0n

to 

	http://YOUR.DOMAIN/route/to/static/file.js/versi0n.js

It means by changing the value in parameter `v` in get request, you are able to get the specific version of a file and which can be specific in a file in a new deployment.

## What This Tool Do

This tool replace `VERSION` in anything like

	"/absolute/route/to/static/file.js?v=VERSION"

in your source code with the last 10 characters of hex of md5 digest of the file `/absolute/route/to/static/file.js`. The string mentioned above can be

	"/absolute/route/to/static/file.js?v=versi0n890"

and the generated files are stored in the `build` folder, which is going to be deployed.

### Example

#### Sample Source File Directory Structure

	.
	|   cacheinvalidator.py
	|   ciconf.json
	|   index.html
	|   readme.md
	|
	\---js
	        angular-route.js
	        angular-sanitize.js
	        angular.js
	        app.js
	        controllers.js

#### Sample Content in `index.html`

	...
	<script src="/js/angular.js?v=VERSION"></script>
	<script src="/js/angular-sanitize.js?v=VERSION"></script>
	<script src="/js/app.js?v=VERSION"></script>
	<script src="/js/controllers.js?v=VERSION"></script>
	...

#### Sample config in `ciconf.json`

	{
		"include": [
			"."
		],
		"entry": [
			"index.html"
		],
		"suffix": [
			".js",
			".css",
			".html"
		],
		"exclude": [
			"build",
			"dependencies"
		],
		"unchange": [
			"dependencies"
		]
	}

#### config explanation

1. `include`: optional, the list of the directories being proccessed.
2. `entry`: the list of file being used as entrance of site, which is usually not cached in browser.
3. `suffix`: the list of suffix of files needed to be proccessed.
4. `exclude`: the list of the directories **NOT** being proccessed.
5. `unchange`: the list of the directories will be included in the `build` folder. However, they are not being proccessed.

#### Sample Output Directory Structure

	|   cacheinvalidator.py
	|   ciconf.json
	|   index.html
	|   readme.md
	|
	+---build
	|   |   index.html
	|   |
	|   +---dependencies
	|   \---js
	|       +---angular-route.js
	|       |       75b5e2426f.js
	|       |
	|       +---angular-sanitize.js
	|       |       79ec2f68f0.js
	|       |
	|       +---angular.js
	|       |       656cada805.js
	|       |
	|       +---app.js
	|       |       1945f74118.js
	|       |
	|       \---controllers.js
	|               831de16c03.js
	|
	+---dependencies
	\---js
	        angular-route.js
	        angular-sanitize.js
	        angular.js
	        app.js
	        controllers.js

#### Sample Content in `build/index.html`

	...
	<script src="/js/angular.js?v=656cada805"></script>
	<script src="/js/angular-sanitize.js?v=79ec2f68f0"></script>
	<script src="/js/app.js?v=1945f74118"></script>
	<script src="/js/controllers.js?v=831de16c03"></script>
	...

# Convenience of Using This Tool

When developing and debuging, your don't need to build and you can do whatever as usually. You just need to add the nginx config mentioned above in your production environment.