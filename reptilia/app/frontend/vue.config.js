const path = require("path")

module.exports = {
    outputDir: path.resolve(__dirname, './../templates'),
    assetsDir: './../static',
    pluginOptions: {
        quasar: {}
    },
    transpileDependencies: [
        /[\\/]node_modules[\\/]quasar[\\/]/
    ],
    configureWebpack:{
        module: {
            rules: [
                {
                    test: /\.pug$/,
                    loader: 'pug-plain-loader'
                },
                // {
                //     test: /\.scss$/,
                //     use: [
                //         'vue-style-loader',
                //         'css-loader',
                //         'sass-loader'
                //     ]
                // }
            ]
        }
    }
}
