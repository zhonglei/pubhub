%name, listPinnedArticleStr = args

<!DOCTYPE html>
<html lang="en">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8"> 
        <title>Scooply</title>
        <meta name="generator" content="Bootply" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">		
    </head>
    
	<body>
	
		<p> Hello {{name}}, </p>
		<p> This week's top-notch bioscience papers are ready to view. Enjoy!!</p>
		<p> We are persistently working towards improving our results quality. 
		If the displayed results do not match your expectation, or if you have any
		suggestions, we would greatly appreciate your feedback by replying to this 
		email. </p>	
		<p>
			<b>What's New </b> - now you can pin your favorite papers and view them <a href="{{listPinnedArticleStr}}">here</a>.
		</p>

		<p> Your Scooply team <br>
		<em> Scooply \'skoop-li\ : timely, relevant and potentially game-changing </em></p>

		<hr>

%listQueryPhrase = [row[0] for row in rows] #first element is queryPhrase
%listQueryPhrase = list(set(listQueryPhrase)) # distinct
%#bring to print Nature, Science and Cell
%if 'Cell' in listQueryPhrase:
%	listQueryPhrase.insert(0, listQueryPhrase.pop(listQueryPhrase.index('Cell')))
%end
%if 'Science' in listQueryPhrase:
	%listQueryPhrase.insert(0, listQueryPhrase.pop(listQueryPhrase.index('Science')))
%end
%if 'Nature' in listQueryPhrase:
	%listQueryPhrase.insert(0, listQueryPhrase.pop(listQueryPhrase.index('Nature')))
%end

		<div class="content_main">
			
			<h3>
				This week's summary
			</h3>
					
			<h4>
				<ul>
%for q in listQueryPhrase: 
	%lenq = len([row for row in rows if row[0] == q])
					<li><a href="#{{q}}">{{q}} ({{lenq}} new)</a></li>
%end
				</ul>
			</h4>		
						
		
%for q in listQueryPhrase:

	%rows2 = [row for row in rows if row[0] == q]
	
			<h3>
				{{q}}<a name="{{q}}"></a>
			</h3>
					
	%for row in rows2:
		%queryPhrase, ArticleTitle, JournalTitle, dayStr, authorField, affiliation, articleLinkStr = row
	
				<div class="article_info">
					<h4> 
						<a href="{{articleLinkStr}}" target="_blank">{{ArticleTitle}}</a> <br>
						{{authorField}} <br>
						{{dayStr}} in <span class="label label-default">{{JournalTitle}}</span> <br>
			%if queryPhrase != JournalTitle:
						Alert on <span class="label label-default">{{queryPhrase}}</span>
			%end
					</h4>
				</div>
	%end	

%end

			
		</div><!-- content_main-->

    </body>

</html>