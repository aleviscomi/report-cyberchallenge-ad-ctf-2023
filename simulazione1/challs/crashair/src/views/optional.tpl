% include('header.tpl', title='Optionals', descr='Here\'s the optionals we offer')

<div class="card border-secondary mb-8">
    <div class="card-header">Make a request</div>
    <div class="card-body">
        <p class="card-text">Fill the form with a specific optional and we will provide it for you.</p>
        <form action="/optionals/{{op['ID']}}" method="post">
            <label for="type">Type of optional:</label>
            <select name="type" id="type" {{'' if edit else 'disabled' }}>
                <option value="1" {{'selected' if op['type']=='Custom-made dessert' else '' }}>Custom-made dessert</option>
                <option value="2" {{'selected' if op['type']=='On-demand movie' else '' }}>On-demand movie</option>
                <option value="3" {{'selected' if op['type']=='Other...' else '' }}>Other...</option>
            </select>

            <div class="form-group">
                <label for="instructions">Additional notes:</label>
                <textarea class="form-control" name="instructions" id="instructions" rows="3" required {{'' if edit else 'disabled' }}>{{ op['instructions'] if edit or op['password'] is None else '' }}</textarea>
            </div>

            <div class="form-group">
                <label for="password">Type in password to make it private:</label>
                <input type="password" class="form-control" name="password" id="password" placeholder="Password" {{'' if edit else 'disabled' }} value="{{ op['password'] if op['password'] else '' }}">
            </div>

            % if edit:
            <button type="submit" class="btn btn-primary form-control">Submit</button>
            % else:
            <a class="btn btn-lg btn-block btn-primary" href="/optionals" role="button">Back</a>
            % end
        </form>
    </div>
</div>

% include('footer.tpl')
