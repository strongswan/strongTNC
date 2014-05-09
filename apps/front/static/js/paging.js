$(document).ready(function() {
    // initialize paging
    // static initializer see bottom of file
    Pager.init();
});

var Pager = function() {

    // initializer for the instance
    this.init = function() {
        // param names
        this.pageParam = 'page';
        this.filterParam = 'filter';
        if(Pager.count != 1) {
            this.pageParam += this.uid;
            this.filterParam += this.uid;
        }

        // get setup values
        this.template = this.$ctx.data('template');
        this.pageSize = this.$ctx.data('page-size');
        this.filter = this.$ctx.data('filter');
        this.currentPageIdx = 0;
        this.listProducer = this.$ctx.data('list-producer');
        this.statProducer = this.$ctx.data('stat-producer');
        this.varName = this.$ctx.data('var-name');
        this.urlName = this.$ctx.data('url-name');

        // get containers and buttons
        this.$buttonContainer = $('.paging-buttons', this.$ctx);
        this.$nextButton = $('.paging-next', this.$ctx);
        this.$prevButton = $('.paging-prev', this.$ctx);
        this.$currentPageElem = $('.paging-current', this.$ctx);
        this.$pageCountElem = $('.paging-page-count', this.$ctx);
        this.$contentContainer = $('.paged-content', this.$ctx);

        // bind events
        this.$nextButton.on('click', this.next.bind(this));
        this.$prevButton.on('click', this.prev.bind(this));

        // add the filter functionality, if a filter is needed
        if(this.filter) {
            this.addFilter();
        }

        // if url parameter were set, get them
        this.grabURLParams();

        // get initial page
        this.getPage();

        $(window).on('hashchange', function() {
            if(!this.loading && this.hasURLParam()) {
                if(this.grabURLParams()) {
                    this.getPage();
                }
            }
        }.bind(this));
    };

    this.grabURLParams = function() {
        var changed = false;
        var currPageIdx = parseInt(this.getURLParam(this.pageParam));
        if(!isNaN(currPageIdx)) {
            var idxChanged = this.currentPageIdx != currPageIdx;
            this.currentPageIdx = currPageIdx;
        }
        var filter = this.getURLParam(this.filterParam);
        if(filter) {
            var filterChanged = this.getFilterQuery() != filter;
            this.$filterInput.val(filter);
        }
        return changed || idxChanged || filterChanged;
    };

    // grab next page
    this.next = function() {
        if(this.currentPageIdx == this.pageCount - 1 || this.loading) {
            return;
        }
        ++this.currentPageIdx;
        this.getPage();
    };

    // grab previous page
    this.prev = function() {
        if(this.currentPageIdx == 0 || this.loading) {
            return;
        }
        --this.currentPageIdx;
        this.getPage();
    };

    this.getPage = function() {
        if(!this.isPageIdxInRange()) {
            this.currentPageIdx = 0;
        }
        var filterQuery = this.getFilterQuery();
        var paramObject = this.getParamObject(filterQuery);
        this.loading = true;
        Dajaxice.apps.front.paging(this.pagingCallback.bind(this), paramObject);
    };

    this.statsUpdate = function(data) {
        this.currentPageIdx = data.current_page;
        this.pageCount = data.page_count;
        this.hideButtons();
        this.updateStatus();
    };

    this.pagingCallback = function(data) {
        this.statsUpdate(data);
        this.$contentContainer.html(data.html);
        this.setURLParam(this.pageParam, this.currentPageIdx);
        this.loading = false;
    };

    this.updateStatus = function() {
        this.$currentPageElem.text(this.currentPageIdx + 1);
        this.$pageCountElem.text(this.pageCount);

        if(this.pageCount > 1) {
            if(this.currentPageIdx <= 0) {
                this.$prevButton.prop('disabled', true);
                this.$nextButton.prop('disabled', false);
            } else if(this.currentPageIdx >= this.pageCount - 1) {
                this.$nextButton.prop('disabled', true);
                this.$prevButton.prop('disabled', false);
            } else {
                this.$nextButton.prop('disabled', false);
                this.$prevButton.prop('disabled', false);
            }
        } else {
            this.$nextButton.prop('disabled', true);
            this.$prevButton.prop('disabled', true);
        }

    };

    this.getFilterQuery = function() {
        if(this.$filterInput) {
            if (this.$filterInput.val() != '') {
                return this.$filterInput.val();
            }
        }
        return '';
    };

    this.filterQuery = function() {
        this.currentPageIdx = 0;
        this.getPage();
        this.setURLParam(this.filterParam, this.getFilterQuery());
    };

    this.addFilter = function() {
        this.$filterInput = $('.filter-input', this.$ctx);
        var $filterButton = $('.filter-button', this.$ctx);
        $filterButton.on('click', this.filterQuery.bind(this));
        this.$filterInput.on('keypress', (function(e) {
            if(e.which == 13) {
                this.filterQuery();
            }
        }).bind(this));
    };

    this.hideButtons = function() {
        if(this.pageCount > 1) {
            this.$buttonContainer.removeClass('hidden');
        } else {
            this.$buttonContainer.addClass('hidden');
        }
    };

    this.getParamObject = function(filterQuery) {
        return {
            'template': this.template,
            'list_producer': this.listProducer,
            'stat_producer': this.statProducer,
            'current_page': this.currentPageIdx,
            'var_name': this.varName,
            'url_name': this.urlName,
            'page_size': this.pageSize,
            'filter_query': filterQuery,
            'pager_id': this.uid
        };
    };

    this.setURLParam = function(key, value) {
        var params = HashQuery.getHashQueryObject();
        params[key] = value;
        HashQuery.setHashQueryObject(params);
    };

    this.getURLParam = function(key) {
        var params = HashQuery.getHashQueryObject();
        var param = params[key];
        if(param) {
            return param;
        }
        return '';
    };

    this.hasURLParam = function() {
        var params = HashQuery.getHashQueryObject()
        for (var key in params) {
            if (hasOwnProperty.call(params, key)) return true;
        }
    };

    this.isPageIdxInRange = function() {
        if(this.pageCount) {
            return !!(this.currentPageIdx >= 0 && this.currentPageIdx < this.pageCount);
        }
        return true;
    };
};

// static initalizer
// creates an instance for every paged table found
// on the current page
Pager.init = function() {
    Pager.count = 0;
    $('.ajax-paged').each(function() {
        var p = new Pager();
        p.uid = Pager.count++;
        p.$ctx = $(this);
        p.init();
    });
};
