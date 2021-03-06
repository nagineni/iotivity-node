module.exports = function( grunt ) {

grunt.registerTask( "lint", [ "jshint", "jscs" ] );

grunt.registerTask( "default", [ "test" ] );

grunt.registerTask( "test", [ "lint", "testsuite", "testdist" ] );

grunt.registerTask( "format", [ "esformatter", "clangformat" ] );

};
