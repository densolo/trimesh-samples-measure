const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin')


module.exports = {
    entry: './src/main.ui.tsx',
    mode: 'development',
    output: {
        filename: 'main.ui.bundle.[hash].js',
        path: path.resolve(__dirname, '../sample_measure_lib/resources/ui')
    },
    devServer: {
            contentBase: path.resolve(__dirname, '../sample_measure_lib/resources/ui'),
    },
    plugins: [
        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: 'htmlpage/index.html.template',
            inject: false
        })
    ],
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                test: /\.html$/i,
                loader: 'html-loader',
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            },
        ],
    },
    resolve: {
        modules: [
            path.resolve(__dirname, 'src'),
            path.resolve(__dirname, 'node_modules')
        ],
        extensions: [ '.tsx', '.ts', '.js' ],
    }
};
