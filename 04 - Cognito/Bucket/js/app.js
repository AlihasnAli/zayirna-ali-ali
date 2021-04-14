var CognitoUserPool = AmazonCognitoIdentity.CognitoUserPool;
var CognitoUser = AmazonCognitoIdentity.CognitoUser;
var AuthenticationDetails = AmazonCognitoIdentity.AuthenticationDetails;

var poolData = {
    UserPoolId : 'us-east-1_himhdbMpd',    
    ClientId : '4004hok8je5713b2jql4tjcio0'
};

function registerButton(){
    // get user enteries and store them in their respective variables
    var username;
    var useremail;
    var userrole = document.getElementById("roleInputRegister").value;
    var password;
    
    var errorMes = []

    if( document.getElementById("usernameInputRegister").value){
        username = document.getElementById("usernameInputRegister").value;          
    }else{
        errorMes.push('Please enter a username!<br>'); 
    }  

    
    if(document.getElementById("emailInputRegister").value){
        var useremail = document.getElementById("emailInputRegister").value;        
    }else{
        errorMes.push('Please enter an email!<br>'); 
    }    


    if (document.getElementById("passwordInputRegister").value && document.getElementById("confirmationpassword").value) {        
        
        if (document.getElementById("passwordInputRegister").value != document.getElementById("confirmationpassword").value) {        
            errorMes.push("Passwords Do Not Match!");  
        } else {
            password =  document.getElementById("passwordInputRegister").value;
        } 

    } else {
        errorMes.push("Please enter a password!");  
    }

    
    if (errorMes.length != 0){
        $("#spanRegForm").html(errorMes); 
        
    }else{ 
        // create user pool and store user data in a variable
        var userPool = new CognitoUserPool(poolData);
        
        // declare a array that will hold attributes of user to record a new cognito account
        var attributeList = [];
        
        // store the attribute name and value to be create an email identity
        var dataEmail = {
                Name : 'email',
                Value : useremail 
        };
        
        var dataRole = {
            Name : 'custom:role',
            Value : userrole 
        };

        // create an email identity for the new user
        var attributeEmail = new AmazonCognitoIdentity.CognitoUserAttribute(dataEmail);
        
        // create an role identity for the new user
        var attributeRole = new AmazonCognitoIdentity.CognitoUserAttribute(dataRole);
        
        // store all identities for the new user into the attribute array
        attributeList.push(attributeEmail);
        attributeList.push(attributeRole);
        
        // create a record for the new user to be registered in aws cognito service
        userPool.signUp(username, password, attributeList, null, function(err, result){
                if (err) {
                    if(err.message != 'Unkown error' || JSON.stringify(err) == 'Unkown error' ){
                        // alert(err.message || JSON.stringify(err));
                        $("#spanRegForm").html('');
                        $("#spanRegFormSucc").html('');
                        $("#spanRegForm").html(err.message || JSON.stringify(err));
                        return;
                    }                
                }
                $("#spanRegForm").html('');
                cognitoUser = result.user;
                console.log('user name is ' + cognitoUser.getUsername());
                
                // display notification message to go check email to confirm registration
                $("#spanRegFormSucc").html("Verification link has been sent to user e-mail.");
        });               
        }   
}

function signInButton(){
    // get user credentails and store in variable
    if(document.getElementById("inputUsername").value && document.getElementById("inputPassword").value){
        var authenticationData = {
        Username : document.getElementById("inputUsername").value,
        Password : document.getElementById("inputPassword").value,
        };  
        
        // create user pool and store user data in a variable
        var userPool = new CognitoUserPool(poolData);
        var userData = {
              Username : document.getElementById("inputUsername").value,
              Pool : userPool,
        };
        
        // create cognito authentication object from entered user credentials
        var authenticationDetails = new AuthenticationDetails(authenticationData);
        
        // create a cognito user object
        var cognitoUser = new CognitoUser(userData);
        
        // Check if attempt times is running 
        if(localStorage.getItem("attemptTimeout") !== null ){

            var gDate = new Date();
            var gTime = gDate.getTime();
            if(parseInt(gTime) >= parseInt(localStorage.getItem("attemptTimeout")) ){
                
                localStorage.removeItem("attemptCounter");
                localStorage.removeItem("attemptTimeout");
                cognitoUser.authenticateUser(authenticationDetails, {
                    onSuccess: function (result) {            
                        $("#spanLogFormSucc").html(''); 
                        var accessToken = result.getAccessToken().getJwtToken();
                        console.log(accessToken);
                        cognitoUser.getUserAttributes(function(err, result) {             
                            localStorage.setItem("authUserRole",result[1].getValue());
                            console.log(result[1].getValue());
                        });
                        setTimeout(function(){ window.location.href = "dashboard.html"; }, 500);
                        // localStorage.removeItem("attemptCounter")

                    },
                    onFailure: function(err) {
                        var attemptCounter;
                        if(localStorage.getItem("attemptCounter") === null){
                            attemptCounter = localStorage.setItem("attemptCounter",1);
                            $("#spanLogFormSucc").html(''); 
                            $("#spanLogFormSucc").html(err.message || JSON.stringify(err));                 
                        }else{
                            if(parseInt(localStorage.getItem("attemptCounter")) === 3){
                                // Have excceded number of attempts
                                $("#spanLogFormSucc").html(''); 
                                $("#spanLogFormSucc").html('Please Wait 15 minutes to try again!');
                                setTimeout(function(){ window.location.href = "login.html"; }, 10000);

                                // Save when user is able to re-attempt
                                var tDate = new Date();
                                var tTime = tDate.getTime();
                                var schueledTime = parseInt(tTime)+10000; //900000 Waiut 15 Minutes


                                localStorage.setItem("attemptTimeout", schueledTime)

                            }else{
                                // Trully wrong error
                                incrementCounter = parseInt(localStorage.getItem("attemptCounter")) + 1;
                                attemptCounter = localStorage.setItem("attemptCounter",incrementCounter); 
                                $("#spanLogFormSucc").html(''); 
                                $("#spanLogFormSucc").html(err.message || JSON.stringify(err)); 
                            }
                        }         
                        
                    },
                });
            }else{
                var waitTime = parseInt(localStorage.getItem("attemptTimeout")) - parseInt(gTime);
                readableTime = Math.ceil(parseInt(waitTime)/60000)
                $("#spanLogFormSucc").html('');
                if(parseInt(readableTime) == 1){
                    $("#spanLogFormSucc").html('Please wait '+readableTime+' minute to try again!');
                }else{
                    $("#spanLogFormSucc").html('Please wait '+readableTime+' minutes to try again!');
                } 
                
            }
        }else{
            // authenticate the cognito user by using cognito authentication object
            cognitoUser.authenticateUser(authenticationDetails, {
                onSuccess: function (result) {            
                    $("#spanLogFormSucc").html(''); 
                    var accessToken = result.getAccessToken().getJwtToken();
                    console.log(accessToken);
                    cognitoUser.getUserAttributes(function(err, result) {             
                        localStorage.setItem("authUserRole",result[1].getValue());
                        console.log(result[1].getValue());
                    });
                    setTimeout(function(){ window.location.href = "dashboard.html"; }, 500);
                    // localStorage.removeItem("attemptCounter")

                },
                onFailure: function(err) {
                    var attemptCounter;
                    if(localStorage.getItem("attemptCounter") === null){
                        attemptCounter = localStorage.setItem("attemptCounter",1);
                        $("#spanLogFormSucc").html(''); 
                        $("#spanLogFormSucc").html(err.message || JSON.stringify(err));                 
                    }else{
                        if(parseInt(localStorage.getItem("attemptCounter")) === 3){
                            // Have excceded number of attempts
                            $("#spanLogFormSucc").html(''); 
                            $("#spanLogFormSucc").html('Please wait 15 minutes to try again!');
                            

                            // Save when user is able to re-attempt
                            var tDate = new Date();
                            var tTime = tDate.getTime();
                            var schueledTime = parseInt(tTime)+900000; //900000 Wait 15 Minutes
                            localStorage.setItem("attemptTimeout", schueledTime)

                        }else if(parseInt(localStorage.getItem("attemptCounter")) === 2){
                            incrementCounter = parseInt(localStorage.getItem("attemptCounter")) + 1;
                            attemptCounter = localStorage.setItem("attemptCounter",incrementCounter); 
                            $("#spanLogFormSucc").html(''); 
                            $("#spanLogFormSucc").html('Last attempt, in fail scenario wait 15 minutes to try again!'); 

                        }else{
                            // Trully wrong error
                            incrementCounter = parseInt(localStorage.getItem("attemptCounter")) + 1;
                            attemptCounter = localStorage.setItem("attemptCounter",incrementCounter); 
                            $("#spanLogFormSucc").html(''); 
                            $("#spanLogFormSucc").html(err.message || JSON.stringify(err)); 
                        }
                    }         
                    
                },
            });
        }
    }else{
        var errMs = [];
        if(!document.getElementById("inputUsername").value){
            errMs.push('Please enter a username!<br>');
        }if(!document.getElementById("inputPassword").value){
            errMs.push('Please enter a password!<br>');
        }

        $("#spanLogFormSucc").html(errMs);
    }    
}

function renderName() {
    // create user pool and store user data in a variable
    var userPool = new CognitoUserPool(poolData);
    
    // get current user (from local storage) who is occupating cognito session
    var cognitoUser = userPool.getCurrentUser();
    
    // render user name on the dashboard page
    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
            console.log(cognitoUser);
            $('#usernameDashboard').html(cognitoUser.username);            
        });        
    }
}

function signOutButton() {
    // create user pool and store user data in a variable
    var userPool = new CognitoUserPool(poolData);
    
    // get current user (from local storage) who is occupating cognito session
    var cognitoUser = userPool.getCurrentUser();

    // sign out user if an individual is occupating cognito session
    if (cognitoUser !== null) {
        cognitoUser.signOut();
        window.localStorage.clear();
    }
    authUserRole = null;
    // redirect to welcome page
    window.location.href = "index.html";
}

function verifyPageAccess(){
    // create user pool and store user data in a variable
    var userPool = new CognitoUserPool(poolData);
    
    // get current user (from local storage) who is occupating cognito session
    var cognitoUser = userPool.getCurrentUser();

    // verify no active user 
    if (cognitoUser == null) {
        // redirect to welcome page
        window.location.href = "login.html";        
    } 
}

function verifyPageAuthorization(){
    // create user pool and store user data in a variable
    var userPool = new CognitoUserPool(poolData);
    
    // get current user (from local storage) who is occupating cognito session
    var cognitoUser = userPool.getCurrentUser();

    // verify if the active user is admin
    if (cognitoUser = null) {           
        // not a user 
        window.location.href = "login.html";     
    }
    else{
        // check user role
        var userrole = localStorage.getItem("authUserRole");
        if(userrole != 'admin'){
            window.location.href = "dashboard.html";   
        }            
    }
}

function renderAdminTabs(){    
    // create user pool and store user data in a variable
    var userPool = new CognitoUserPool(poolData);
    
    // get current user (from local storage) who is occupating cognito session
    var cognitoUser = userPool.getCurrentUser();

    // verify if the active user is admin
    if (cognitoUser != null) {           
        // check user role
        var userrole = localStorage.getItem("authUserRole");
        if(userrole == 'admin'){
            $("#dropdownlist").prepend("<a class='dropdown-item' href='register.html'><span class='oi oi-person'></span>&nbsp;&nbsp;Create Users</a>");   
            $("#dropdownlist2").prepend("<a class='dropdown-item' href='register.html'><span class='oi oi-person'></span>&nbsp;&nbsp;Create Users</a>");
        }  
    }    
}