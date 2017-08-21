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

        function calculateSums(target_array) {
            output_list = [];
            set = new Set(target_array);
            target_array = target_array.sort();

            angular.forEach(set, function(item) {
                var count = target_array.reduce(function(n, val) {
                    return n + (val === item);
                }, 0);
                output_list.push([item, count]);
            });

            // Sort the array, based on the second element:
            output_list.sort(function(first, second) {
                return second[1] - first[1];
            });
            return output_list;
        };

        function calculateSummaryValues(users) {
            ages = []
            sexes = []
            unprocessed_colors = []
            angular.forEach(users, function(user) {
                ages.push(user.age);
                sexes.push(user.gender);
                angular.forEach(user.colors, function(color) {
                    unprocessed_colors.push(color.color);
                });
            });

            $scope.summary.gender = calculateSums(sexes);

            colors = calculateSums(unprocessed_colors);
            $scope.summary.colors = colors.slice(0, 3);

            var age_sum = ages.reduce(function(a, b) { return a + b; });
            $scope.summary.age = age_sum / ages.length;
        };

        $scope.reload = function () {
            var user_response = UserService.query();
            if (angular.isUndefined($scope.users)){
                $scope.users = user_response;
            } else{
                $q.all([user_response.$promise]).then(function(user_data) {
                    $scope.users = user_data[0];
                    calculateSummaryValues($scope.users);
                });
            };
        };
        $scope.summary = {};
        $scope.reload();
        $interval($scope.reload, 1000);
    }
]);
