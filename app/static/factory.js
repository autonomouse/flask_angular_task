var hjapp = angular.module('HjApp.admin', ['ngResource'])

hjapp.factory('UserService', ['$resource', function($resource) {
    return $resource('/api/v1/users/:user', {user: "@user"});
    //return $resource('/api/v1/users/:id');
}]);
