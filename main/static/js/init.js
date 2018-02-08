/**
 * Create a citynames Bloodhound
 *
 * @type {Bloodhound}
 */

var neighborhoods = new Bloodhound({
   datumTokenizer : Bloodhound.tokenizers.obj.whitespace('name'),
   queryTokenizer : Bloodhound.tokenizers.whitespace,
   prefetch       : {
       url    : 'static/data/neighborhoods.json',
       filter : function (list)
       {
           return $.map(list, function (neighborhood)
           {
               return {name : neighborhood};
           });
       }
   }
});
neighborhoods.initialize();

var neighborhoods_r = new Bloodhound({
   datumTokenizer : Bloodhound.tokenizers.obj.whitespace('name'),
   queryTokenizer : Bloodhound.tokenizers.whitespace,
   prefetch       : {
       url    : 'static/data/neighborhoods_r.json',
       filter : function (list)
       {
           return $.map(list, function (neighborhood)
           {
               return {name : neighborhood};
           });
       }
   }
});
neighborhoods_r.initialize();

var attributes = new Bloodhound({
   datumTokenizer : Bloodhound.tokenizers.obj.whitespace('name'),
   queryTokenizer : Bloodhound.tokenizers.whitespace,
   prefetch       : {
       url    : 'static/data/attributes.json',
       filter : function (list)
       {
           return $.map(list, function (attribute)
           {
               return {name : attribute};
           });
       }
   }
});
attributes.initialize();

var categories = new Bloodhound({
   datumTokenizer : Bloodhound.tokenizers.obj.whitespace('name'),
   queryTokenizer : Bloodhound.tokenizers.whitespace,
   prefetch       : {
       url    : 'static/data/categories.json',
       filter : function (list)
       {
           return $.map(list, function (category)
           {
               return {name : category};
           });
       }
   }
});
categories.initialize();

var boroughs = new Bloodhound({
   datumTokenizer : Bloodhound.tokenizers.obj.whitespace('name'),
   queryTokenizer : Bloodhound.tokenizers.whitespace,
   prefetch       : {
       url    : 'static/data/boroughs.json',
       filter : function (list)
       {
           return $.map(list, function (borough)
           {
               return {name : borough};
           });
       }
   }
});
boroughs.initialize();

var transports = new Bloodhound({
   datumTokenizer : Bloodhound.tokenizers.obj.whitespace('name'),
   queryTokenizer : Bloodhound.tokenizers.whitespace,
   prefetch       : {
       url    : 'static/data/transports.json',
       filter : function (list)
       {
           return $.map(list, function (transport)
           {
               return {name : transport};
           });
       }
   }
});
transports.initialize();

var amenities = new Bloodhound({
   datumTokenizer : Bloodhound.tokenizers.obj.whitespace('name'),
   queryTokenizer : Bloodhound.tokenizers.whitespace,
   prefetch       : {
       url    : 'static/data/amenities.json',
       filter : function (list)
       {
           return $.map(list, function (amenity)
           {
               return {name : amenity};
           });
       }
   }
});
amenities.initialize();


/**
 * Create a cities Bloodhound
 *
 * @type {Bloodhound}
 */
// var cities = new Bloodhound({
//     datumTokenizer : Bloodhound.tokenizers.obj.whitespace('text'),
//     queryTokenizer : Bloodhound.tokenizers.whitespace,
//     prefetch       : 'static/data/cities.json'
// });
// cities.initialize();

var beds = new Bloodhound({
    datumTokenizer : Bloodhound.tokenizers.obj.whitespace('text'),
    queryTokenizer : Bloodhound.tokenizers.whitespace,
    prefetch       : 'static/data/beds.json'
});
beds.initialize();

var baths = new Bloodhound({
    datumTokenizer : Bloodhound.tokenizers.obj.whitespace('text'),
    queryTokenizer : Bloodhound.tokenizers.whitespace,
    prefetch       : 'static/data/baths.json'
});
baths.initialize();

/**
 * Typeahead
 */

var nei = $('#neighborhood-typeahead input.typehead-input');
nei.materialtags({
   freeInput:false,
   typeaheadjs : {
       name       : 'neighborhoods',
       displayKey : 'name',
       valueKey   : 'name',
       source     : neighborhoods.ttAdapter()
   }
});

var nei_r = $('#neighborhood_r-typeahead input.typehead-input');
nei_r.materialtags({
   freeInput:false,
   typeaheadjs : {
       name       : 'neighborhoods_r',
       displayKey : 'name',
       valueKey   : 'name',
       source     : neighborhoods_r.ttAdapter()
   }
});

var cat = $('#category-typeahead input.typehead-input');
cat.materialtags({
   freeInput:false,
   typeaheadjs : {
       name       : 'categories',
       displayKey : 'name',
       valueKey   : 'name',
       source     : categories.ttAdapter()
   }
});

var attr = $('#attribute-typeahead input.typehead-input');
attr.materialtags({
   freeInput:false,
   typeaheadjs : {
       name       : 'attributes',
       displayKey : 'name',
       valueKey   : 'name',
       source     : attributes.ttAdapter()
   }
});


var bor = $('#borough-typeahead input.typehead-input');
bor.materialtags({
   freeInput:false,
   typeaheadjs : {
       name       : 'boroughs',
       displayKey : 'name',
       valueKey   : 'name',
       source     : boroughs.ttAdapter()
   }
});

var tra = $('#transport-typeahead input.typehead-input');
tra.materialtags({
   freeInput:false,
   typeaheadjs : {
       name       : 'transports',
       displayKey : 'name',
       valueKey   : 'name',
       source     : transports.ttAdapter()
   }
});

var ame = $('#amenity-typeahead input.typehead-input');
ame.materialtags({
   freeInput:false,
   typeaheadjs : {
       name       : 'amenities',
       displayKey : 'name',
       valueKey   : 'name',
       source     : amenities.ttAdapter()
   }
});



var bed = $('#bed_objects input.object-tag-input');
bed.materialtags({
    itemValue   : 'value',
    itemText    : 'text',
    typeaheadjs : {
        name       : 'beds',
        displayKey : 'text',
        source     : beds.ttAdapter()
    }
});

var bat = $('#bath_objects input.object-tag-input');
bat.materialtags({
    itemValue   : 'value',
    itemText    : 'text',
    typeaheadjs : {
        name       : 'baths',
        displayKey : 'text',
        source     : baths.ttAdapter()
    }
});


$('select').not('.disabled').material_select();

// $('.collapsible').collapsible();
