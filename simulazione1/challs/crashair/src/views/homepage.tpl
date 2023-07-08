% include('header.tpl', title='Home', descr='A cheap flight')

%if username is None:
    <style>
        
    .form-signin {
    width: 100%;
    max-width: 330px;
    padding: 15px;
    margin: auto;
    }
    .form-signin .checkbox {
    font-weight: 400;
    }
    .form-signin .form-control {
    position: relative;
    box-sizing: border-box;
    height: auto;
    padding: 10px;
    font-size: 16px;
    }
    .form-signin .form-control:focus {
    z-index: 2;
    }
    .form-signin input[type="text"] {
    margin-bottom: -1px;
    border-bottom-right-radius: 0;
    border-bottom-left-radius: 0;
    }
    .form-signin input[type="password"] {
    margin-bottom: 10px;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
    }
    </style>
    <form method="post" class="form-signin">
        <h1 class="h3 mb-3 font-weight-normal">Please sign in or register</h1>

        <label for="username" class="sr-only">Username</label>
        <input type="text" name="username" id="username" class="form-control" placeholder="User name" required autofocus>

        <label for="password" class="sr-only">Password</label>
        <input type="password" name="password" id="password" class="form-control" placeholder="Password" required>

        <button class="btn btn-lg btn-primary btn-block" type="submit" formaction="/register">REGISTER</button>
        <button class="btn btn-lg btn-primary btn-block" type="submit" formaction="/login">LOGIN</button>
    </form>
%else:
    <h1>Hello {{ username }}!</h1>
    <div class="card-deck mb-3 text-center">
        <div class="card mb-4 shadow-sm">
            <div class="card-header">
                <h4 class="my-0 font-weight-normal">Step 1</h4>
            </div>
            <div class="card-body">
                <h1 class="card-title pricing-card-title">Optionals</h1>
                <ul class="list-unstyled mt-3 mb-4">
                    <li>Request a customized optional</li>
                    <li>or request one made</li>
                    <li>by someone else!</li>
                    <li>Discover the possibilities...</li>
                </ul>
                <a class="btn btn-lg btn-block btn-primary" href="/optionals" role="button">Manage</a>
            </div>
        </div>
        <div class="card mb-4 shadow-sm">
            <div class="card-header">
                <h4 class="my-0 font-weight-normal">Step 2</h4>
            </div>
            <div class="card-body">
                <h1 class="card-title pricing-card-title">Reservation</h1>
                <ul class="list-unstyled mt-3 mb-4">
                    <li>Reserve your flight right now!</li>
                    <li>Seat reservation, online check-in</li>
                    <li>and custom optionals are sold</li>
                    <li>separately.</li>
                </ul>
                <a class="btn btn-lg btn-block btn-primary" href="/reservations" role="button">Manage</a>
            </div>
        </div>
        <div class="card mb-4 shadow-sm">
            <div class="card-header">
                <h4 class="my-0 font-weight-normal">Step 3</h4>
            </div>
            <div class="card-body">
                <h1 class="card-title pricing-card-title">Checkout</h1>
                <ul class="list-unstyled mt-3 mb-4">
                    <li>Confirm your reservation</li>
                    <li>or if you are in a hurry</li>
                    <li>copy the reservation made </li>
                    <li>by someone else.</li>
                </ul>
                <a class="btn btn-lg btn-block btn-primary" href="/checkout" role="button">Checkout</a>
            </div>
        </div>
    </div>
%end

% include('footer.tpl')
