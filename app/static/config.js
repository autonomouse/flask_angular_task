var hjapp = angular.module('HjApp', [
    'ngRoute',
    'ngResource',
    'HjApp.admin']);

hjapp.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
}]);

