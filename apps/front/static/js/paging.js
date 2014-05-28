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
        this.config = this.$ctx.data('config');
        this.filter = this.$ctx.data('filter');
        this.args = this.$ctx.data('args');
        this.currentPageIdx = 0;

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

        // register hashChanged events
        HashQuery.addChangedListener(this.pageParam, this.grabPageParam.bind(this));
        HashQuery.addChangedListener(this.filterParam, this.grabFilterParam.bind(this));

        // get initial page
        this.initial = true;
        this.getInitalURLParam();
        this.getPage();

    };

    this.grabPageParam = function(key, value) {
        var currPageIdx = parseInt(value);
        if(!isNaN(currPageIdx)) {
            var idxChanged = this.currentPageIdx != currPageIdx;
            this.currentPageIdx = currPageIdx;
        }
        if(idxChanged) {
            this.getPage();
        }
    };

    this.grabFilterParam = function(key, value) {
        var filter = value;
        if(filter) {
            var filterChanged = this.getFilterQuery() != filter;
            this.$filterInput.val(filter);
        }
        if(filterChanged) {
            this.getPage();
        }
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
        this.setURLParam(this.pageParam, this.currentPageIdx, this.initial);
        this.initial = false;
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
        this.setURLParam(this.filterParam, this.getFilterQuery(), false);
    };

    this.addFilter = function() {
        this.$filterInput = $('.filter-input', this.$ctx);
        var $filterButton = $('.filter-button', this.$ctx);
        var $filterClearButton = $('.filter-clear-button', this.$ctx);
        $filterButton.on('click', this.filterQuery.bind(this));
        $filterClearButton.on('click', (function() {
            this.$filterInput.val('');
            this.filterQuery();
        }).bind(this));
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
            'config_name': this.config,
            'current_page': this.currentPageIdx,
            'filter_query': filterQuery,
            'pager_id': this.uid,
            'producer_args': this.args
        };
    };

    this.setURLParam = function(hashKey, hashValue, avoidHistory) {
        var hashKeyObj = {};
        hashKeyObj[hashKey] = hashValue;
        HashQuery.setHashKey(hashKeyObj, false, avoidHistory);
    };

    this.getInitalURLParam = function() {
        var params = HashQuery.getHashQueryObject();
        for (var key in params) {
            if (hasOwnProperty.call(params, key)) {
                if(key == this.pageParam) {
                    var currIdx = parseInt(params[key]);
                    if(!isNaN(currIdx)) {
                        this.currentPageIdx = currIdx;
                    }
                }
                if(key == this.filterParam) {
                    this.$filterInput.val(params[key]);
                }
            }
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
