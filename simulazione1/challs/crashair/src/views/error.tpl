% include('header.tpl', title='Error', descr='ooops')
<div class="container mt-5 p-5">

    <h2>Error: {{ code }}</h2>
    <div class="card">
    <pre class="card-body">{{ message }}</pre>
    </div>
    </p>
</div>
% include('footer.tpl')
