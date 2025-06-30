module.exports = {
    root: true,
    env: {
        node: true
    },
    extends: [
        'plugin:vue/vue3-essential',
        'eslint:recommended'
    ],
    parserOptions: {
        parser: '@babel/eslint-parser',
        requireConfigFile: false,
        babelOptions: {
            presets: ['@babel/preset-env']
        }
    },
    ignorePatterns: [
        'public/**/*',
        'dist/**/*',
        'node_modules/**/*'
    ]
} 