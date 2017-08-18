var hjapp = angular.module('HjApp.admin', ['ngRoute', 'UserService'])

hjapp.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'static/admin/admin.html',
            controller: 'controller',
            controllerAs:'controller'
        })
}]);

hjapp.controller('controller', [
    '$scope', function($scope) {
        $scope.users = UserService.query();
    }
]);
