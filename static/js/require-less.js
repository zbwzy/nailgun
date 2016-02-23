/*
 * Copyright 2014 Mirantis, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
**/

define(['jquery', 'lessLibrary'], function($, less) {
    'use strict';

    return {
        load: function(name, req, onLoad) {
           /* var skiname=$.cookie('skin');
            if(skiname=="blue")
            {
             name="/static/css/styles-blue";
            }
            if(skiname=="white")
            {
              name="/static/css/styles-white";
            }*/
            name="/static/css/styles";
            var url = req.toUrl(name + '.less');
            var link = $('<link/>', {href: url, rel: 'stylesheet/less'});
            link.appendTo('head');
            less.sheets.push(link[0]);
            less.refresh();
            onLoad();
        }
    };
});
