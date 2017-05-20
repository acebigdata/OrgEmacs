var data = source.data;
var filetext = 'company_name,ticker,country,region,av_sector,year,metric\n';
for (i=0; i < data['company_name'].length; i++) {
    var currRow = [data['company_name'][i].toString(),
                   data['ticker'][i].toString(),
                   data['country'][i].toString(),
                   data['region'][i].toString(),
                   data['av_sector'][i].toString(),
                   data['year'][i].toString(),
                   data['metric'][i].toString().concat('\n')];

    var joined = currRow.join();
    filetext = filetext.concat(joined);
}

var filename = 'data_result.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename);
}

else {
    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))
}
