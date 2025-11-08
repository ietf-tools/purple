// Documentation of options at https://github.com/vue-styleguidist/vue-styleguidist/tree/dev/packages/vue-docgen-cli
module.exports = {
  componentsRoot: '../client/app/components', // the folder where CLI will start searching for components.
  components: '**/[A-Z]*.vue', // the glob to define what files should be documented as components (relative to componentRoot)
  outDir: 'output' // folder to save components docs in (relative to the current working directry)
}
