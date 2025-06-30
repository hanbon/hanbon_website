module.exports = {
  presets: [
    ['@babel/preset-env', {
      useBuiltIns: 'entry',
      corejs: 3
    }],
    '@vue/cli-plugin-babel/preset'
  ],
  env: {
    development: {
      // 开发环境特定配置
      sourceMaps: true,
      retainLines: true
    },
    production: {
      // 生产环境优化
      minified: true
    }
  }
}
