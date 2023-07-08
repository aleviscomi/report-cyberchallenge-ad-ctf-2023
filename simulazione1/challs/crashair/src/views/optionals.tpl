% include('header.tpl', title='Optionals', descr='Here\'s the optionals we offer')

<div class="card border-secondary mb-8">
    <div class="card-header">Make a request</div>
    <div class="card-body">
        <p class="card-text">Fill the form with a specific optional and we will provide it for you.</p>
        <form action="/optionals" method="post">
            <label for="type">Type of optional:</label>
            <select name="type" id="type">
                <option value="1">Custom-made dessert</option>
                <option value="2">On-demand movie</option>
                <option value="3">Other...</option>
            </select>

            <div class="form-group">
                <label for="instructions">Additional notes:</label>
                <textarea class="form-control" name="instructions" id="instructions" rows="3" required></textarea>
            </div>
            
            <div class="form-group">
                <label for="password">Type in password to make it private:</label>
                <input type="password" class="form-control" name="password" id="password">
            </div>
            <button type="submit" class="btn btn-primary form-control">Submit</button>
        </form>
    </div>
</div>


<table class="table">
    <thead>
        <tr>
            <th scope="col">#</th>
            <th scope="col">Author</th>
            <th scope="col">Type</th>
            <th scope="col">Instructions</th>
            <th scope="col">Private</th>
            <th scope="col">Submission Date</th>
            <th scope="col">Actions</th>
        </tr>
    </thead>
    <tbody>
        
    % for op in optionals:
    <tr class="{{ 'table-primary' if op['owner'] == username else '' }}">
        <th scope="row">{{ op['ID'] }}</th>
        <td>{{ op['owner'] }}</td>
        <td>{{ op['type'] }}</td>
        % if op['password'] is None or op['owner'] == username:
        <td>{{ op['instructions'] }}</td>
        % else:
        <td> --- </td>
        % end

        % if op['password'] is None:
        <td> NO </td>
        % else:
        <td> YES </td>
        % end
        
        <td>{{ op['ts'] }}</td>
        <td><a href="/optionals/{{ op['ID'] }}">{{'edit' if op['owner'] == username else 'info'}}</a></td>
    </tr>
    % end
    </tbody>
</table>

% include('footer.tpl')
