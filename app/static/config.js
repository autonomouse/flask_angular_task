var hjapp = angular.module('HjApp', [
    'ngRoute',
    'HjApp.admin']);

hjapp.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
}]);

