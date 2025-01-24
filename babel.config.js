module.exports = {
    presets: [
        '@vue/cli-plugin-babel/preset',
        ['@babel/preset-env', {
            'targets': {
                'browsers': ["> 1%", "last 2 versions", "not ie <= 8"]
            }
        }]
    ]
}; 