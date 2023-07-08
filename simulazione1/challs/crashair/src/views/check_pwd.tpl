% include('header.tpl', title='Checkout', descr='Get your ticket')

<div class="card border-secondary mb-8">
    <div class="card-header">Insert password</div>
    <div class="card-body">
        <p class="card-text">The optional you are trying to checkout is private. Please provide the password to continue.</p>
        <form action="/checkout/check_pwd" method="post">
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" class="form-control" name="password" id="password">
            
                <button type="submit" class="form-control">Submit</button>
            </div>
        </form>
    </div>
</div>

% include('footer.tpl')
