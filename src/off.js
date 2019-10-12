var easymidi = require('easymidi');
var inputs = easymidi.getInputs();
console.log(inputs);


var qchan = 0;
var qu = new easymidi.Output('QU-32:QU-32 MIDI 1 20:0');
qu.send('cc', { controller: 0x63, value: 0x00, channel: qchan });
qu.send('cc', { controller: 0x62, value: 0x5f, channel: qchan });
qu.send('cc', { controller: 0x06, value: 0x00, channel: qchan });
qu.send('cc', { controller: 0x26, value: 0x00, channel: qchan });
