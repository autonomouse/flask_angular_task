hjapp.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'static/admin/admin.html',
            controller: 'controller',
            controllerAs:'controller'
        })
}]);

hjapp.controller('controller', [
    '$scope', 'UserService', function($scope, UserService) {
        $scope.users = UserService.query();
    }
]);
