var hjapp = angular.module('HjApp.admin', ['ngRoute'])

hjapp.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/survey', {
            templateUrl: 'static/admin/admin.html',
            controller: 'controller',
            controllerAs:'controller'
        })
        .when('/admin', {
            templateUrl: 'static/admin/admin.html',
            controller: 'controller',
            controllerAs:'controller'
        })
        .otherwise({
            redirectTo: '/survey'
        });
}]);

hjapp.controller('controller', [
    '$scope', function($scope) {
        $scope.message = "HOTJAR";
    }
]);
