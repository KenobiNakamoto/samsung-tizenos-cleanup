/* Family Home's compact grouping on top of CleanFrame's renderer. ES5. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.FamilyLayout = factory();
}(this, function () {
  'use strict';
  function geometry(ids, sizes) {
    var cells = [], x = 0, pending = [], width = 224, height = 200, gap = 12;
    function flush() {
      if (!pending.length) return;
      pending.forEach(function (id, i) { cells.push({id:id, x:x + (i % 2) * 106, y:Math.floor(i / 2) * 106, w:94, h:94, small:true}); });
      x += height + gap; pending = [];
    }
    ids.forEach(function (id) {
      if (sizes[id] === 'compact') { pending.push(id); if (pending.length === 4) flush(); }
      else { flush(); cells.push({id:id, x:x, y:0, w:width, h:height, small:false}); x += width + gap; }
    });
    flush();
    cells.push({id:'__apps', x:x, y:0, w:height, h:height, kind:'apps'}); x += height + gap;
    cells.push({id:'__add', x:x, y:0, w:64, h:height, kind:'add'}); x += 64;
    return {cells:cells, width:x};
  }
  function neighbor(cells, id, direction) {
    var source = cells.filter(function (c) {return c.id === id;})[0], vertical = direction === 'up' || direction === 'down';
    var sign = direction === 'up' || direction === 'left' ? -1 : 1, best = null, bestScore = Infinity;
    if (!source) return null;
    cells.forEach(function (c) {
      if (c === source) return;
      var primary = (vertical ? c.y + c.h / 2 - source.y - source.h / 2 : c.x + c.w / 2 - source.x - source.w / 2) * sign;
      var secondary = Math.abs(vertical ? c.x + c.w / 2 - source.x - source.w / 2 : c.y + c.h / 2 - source.y - source.h / 2);
      if (primary < 5 || vertical && secondary > 5) return;
      var score = primary + secondary * 3;
      if (score < bestScore) {best = c.id; bestScore = score;}
    });
    return best;
  }
  return {geometry:geometry, neighbor:neighbor};
}));
