if (window.location.href.indexOf("?") != -1) {
	search();
}
function search() {
	document.getElementById("results").innerHTML = "Searching...";
	var url = "searching.json";
	var xmlhttp = new XMLHttpRequest();
	var andButton = document.getElementById("and")
	xmlhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			var text = JSON.parse(this.responseText);
			var terms = getTerms();
			if (terms.length == 1) {arr = oneTermSearch(text, terms);}
			else {
				if (andButton.checked) {arr = andSearch(text, terms);}
				else {arr = orSearch(text, terms);}
			}
			display(arr, text, "results", terms);
		}
	};
	xmlhttp.open("GET", url, true);
	xmlhttp.send();
}

// returns array of terms
function getTerms() {
	var markup = ["%E2%80%99", "'", "%c3%bb", "$u", "%27", "'", "\u0294", "''", "\u00ec", "$e", "%29", ")", "%c5%97", ",r",	"%20", "+", "%24", "$", "%25", "%",
	"%3b", " ", "%2cr", ",r"];
	var url = window.location.href;
	url  = url.split("?");
	var searchString = url[1].split("&");
	var andOr = searchString[1].split("=")[1];
	if (andOr == "or") {document.getElementById("or").checked = true}
	var text = searchString[0].split("=")[1];
	for (i = 0; i < markup.length; i += 2) {
		text = text.split(markup[i]).join(markup[i+1]).toLowerCase();
	}
	document.getElementById("term").value = text.split("+").join(" ");
	return text.split("+").filter(function (i) {return i != "";});	
}

// builds array of results containing any search term
// @param arr: raw json array (usually from file)
// @param String[] terms: search terms
function orSearch(arr, terms) {
	var output = new Array;
	for (t in terms) {
		var term = terms[t];
		results = oneTermSearch(arr, term);
		for (r in results) {
			output.push(results[r])
		}
	}
	output.sort(function (a,b) {return parseInt(a[0]) >= parseInt(b[0]);})
	var i = 0;
	while (i < output.length - 1) {
		if (output[i][0] == output[i+1][0]) {
			output[i][1] = output[i][1].concat(output[i+1][1]).sort(function (a,b) {
				return a < b;}).filter(function(item, pos, ary) {
			return !pos || item != ary[pos - 1];
				})
			output = output.filter(function(item, pos, ary) {return pos != i;});
		} else {i++;}
	}
	return output;
}

// builds array of results containing all search terms
function andSearch(arr, terms) {
	var output = new Array;
	num = terms.length - 1;
	for (t in terms) {
		var term = terms[t];
		results = oneTermSearch(arr, term);
		for (r in results) {
			output.push(results[r])
		}
	}
	output.sort(function (a,b) {return parseInt(a[0]) >= parseInt(b[0]);})
	for (var i = num; i < output.length; i++) {
		if (output[i][0] == output[i - num][0]) {
			for (j = i - num; j < i; j++) {
				output[i][1] = output[i][1].concat(output[j][1]);
			}
			output[i][1] = output[i][1].sort(function (a,b) {
				return a >= b;}).filter(function (item, pos, ary) {
					return (!pos || item != ary[pos - 1]);
			});
		}
	}
	output = output.filter(function (item, pos, ary) {return (pos >= num && item[0] == ary[pos - num][0]);});
	return output;
}

function oneTermSearch(arr, term) {
	text = new Array;
	for (page in arr.terms[term]) {
		text.push([page, arr.terms[term][page]])
	}
	return text;
}

// capitalises first letter
function capitalise(string) {
	if (string.length == 0) {return ""}
	if (string.startsWith("&rsquo;")) {
		return string.replace("&rsquo;", "&#x294;");
	} else {
		return string.charAt(0).toUpperCase() + string.slice(1);
	}
}

function markdown(arr) {
	var marking = ["$a", "&acirc;", "$e", "&ecirc;", "$i", "&icirc;", "$o", "&ocirc;", "$u", "&ucirc;", "$e", "&ecirc;", "$a", "&acirc;", "$e", "&ecirc;", ")a", "&agrave;", ")e", "&egrave;", ")i", "&igrave;", ")o", "&ograve;", ")u", "&ugrave;", "_o", "&#x14d;", "+h", "&#x2b0;", ",c", "&#x255;", ",n", "&#x14b;", "'", "&rsquo;", "''", "&#x294;", "$h", "&#x2b1;", "-i", "&#x268;", "=j", "&#x25f;", "$l", "&#x28e;", "$n", "&#x272;", "$r", "&#x279;", ",r", "&#x157;", "!e", "&#x259;", "-u", "&#x289;", "_u", "&#x16b;"]
	var terms = new Array;
	for (termnum in arr) {
		var term = arr[termnum];
		for (i = 0; i < marking.length; i++) {
			term = term.split(marking[i]).join(marking[++i]);
		}
		terms.push(term);
	}
	return terms;
}
	

// displays results as list
// @param Array arr: results array
function display(arr, data, id, terms) {
	terms = markdown(terms);
	if (arr.length == 0) {
		document.getElementById(id).innerHTML = "Search term(s) not found";
		return;
	}
	var text = "<ol>"
	for (var pagenum in arr) {
		var page = arr[pagenum];
		var link = data.urls[page[0]] + ".html";
		var name = data.names[page[0]];
		var lines = new Array;
		for (linenum in page[1]) {
			var line = data.sentences[page[1][linenum]];
			for (termnum in terms) {
				var term = terms[termnum];
				var replacement = "<strong>" + term + "</strong>"
				line = line.split(term).join(replacement);
				term = capitalise(term);
				replacement = "<strong>" + term + "</strong>"
				line = line.split(term).join(replacement);
			}
			lines.push(line);
		}
		text += "<li><a href=\"" + link + "\">" + name + "</a>: "
		text += lines.join(" &hellip; ") + "</li>"
	}
	text += "</ol>";
	document.getElementById(id).innerHTML = text;
}