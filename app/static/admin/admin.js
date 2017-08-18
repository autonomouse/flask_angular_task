var hjapp = angular.module('HjApp.admin', ['ngRoute'])

hjapp.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/:user', {
            templateUrl: 'static/admin/admin.html',
            controller: 'controller',
            controllerAs:'controller'
        })
}]);

hjapp.controller('controller2', [
    '$scope', function($scope) {
        $scope.message = 'hello'; //$routeParams.user;
    }
]);
