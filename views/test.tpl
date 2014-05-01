<h1>Retrieved Pubmed Articles</h1>
<table>
<tr><th>ID</th><th>PMID</th><th>DOI ID</th><th>Journal</th><th>Title</th></tr>
%for row in rows:
    <tr>
    %for col in row:
        <td>{{col}}</td>
    %end
    </tr>
%end
</table>