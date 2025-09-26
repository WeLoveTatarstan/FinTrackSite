(function(){
  function round(value){
    return Math.round((value + Number.EPSILON) * 10000) / 10000;
  }

  function convert(){
    var amount = parseFloat(document.getElementById('amount').value || '0');
    var from = document.getElementById('from').value;
    var to = document.getElementById('to').value;
    var rates = window.CONVERTER_RATES || {};
    if(!rates[from] || !rates[to]){
      document.getElementById('result').value = '';
      return;
    }
    // Normalize to USD base using provided static rates
    var amountInUsd = amount / rates[from];
    var converted = amountInUsd * rates[to];
    document.getElementById('result').value = round(converted);
  }

  document.getElementById('convertBtn')?.addEventListener('click', convert);
  document.getElementById('amount')?.addEventListener('input', convert);
  document.getElementById('from')?.addEventListener('change', convert);
  document.getElementById('to')?.addEventListener('change', convert);

  // initial calculation
  convert();
})();


