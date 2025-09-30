const withSVGR = require('next-plugin-svgr');

module.exports = withSVGR({
  webpack(config) {
    return config;
  },
});
