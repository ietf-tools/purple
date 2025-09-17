// const path = require('path')

module.exports = {
  componentsRoot: '../client/app/components', // the folder where CLI will start searching for components.
  components: '**/[A-Z]*.vue', // the glob to define what files should be documented as components (relative to componentRoot)
  outDir: 'output' // folder to save components docs in (relative to the current working directry)
  // templates: {
  //   // global component template wrapping all others see #templates
  //   component: require('templates/component'),
  //   events: require('templates/events'),
  //   methods: require('templates/methods'),
  //   props: require('templates/props'),
  //   slots: require('templates/slots'),
  //   // static template to display as a tag if component is functional
  //   functionalTag: '**functional**'
  // }
}
