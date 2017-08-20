hjapp.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'static/admin/admin.html',
            controller: 'controller',
            controllerAs:'controller'
        })
}]);

hjapp.controller('controller', [
    '$scope', 'UserService', '$interval', '$q',
    function($scope, UserService, $interval, $q) {
        $scope.reload = function () {
            var user_response = UserService.query();
            if (angular.isUndefined($scope.users)){
                $scope.users = user_response;
            } else{
                $q.all([user_response.$promise]).then(function(user_data) {
                    $scope.users = user_data[0]
                })
            };
        };
        $scope.reload();
        $interval($scope.reload, 1000);
    }
]);
