# Frontend project

## Thecnologies
	
	vue-cli
	pug

## Requirements

	nvm (sugest for multiples nodes)
	node v14.8.0
	npm v6.14.7

## Install step to step

Install nvm (multiple version node)

	nvm install 14.8.0
	nvm use node

change nodeversion (alternative)

	nvm which 8.0


Cambiar el ip en el archivo `.env` iplocal example: `192.168.1.22`

	VUE_APP_API_URL=http://192.168.1.22:5000/api
	VUE_APP_ROOT_URL=http://192.168.1.22:5000

Comentar las lineas de codigo del archivo `vue.config.js` mode DEVELOPMENT

    // outputDir: path.resolve(__dirname, './../templates'),
    // assetsDir: './../static',


## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```