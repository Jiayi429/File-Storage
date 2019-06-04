from urllib import urlencode
class Pagination(object):
    
    def __init__(self, current_page, total_count, base_url, params, per_page_count=10, max_pager_count=11):
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        if current_page <=0:
            current_page = 1
        self.current_page = current_page
        self.total_count = total_count
 
        # 10 for each page
        self.per_page_count = per_page_count
 
        max_page_num, div = divmod(total_count, per_page_count)
        if div:
            max_page_num += 1
        self.max_page_num = max_page_num
 
        # display 11 page numbers on current page
        self.max_pager_count = max_pager_count
        self.half_max_pager_count = int((max_pager_count - 1) / 2)
 
        # URL
        self.base_url = base_url
 
        # request.GET
        import copy
        params = copy.deepcopy(params)
        get_dict = params.to_dict()
 
        self.params = get_dict
 
    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_count
 
    @property
    def end(self):
        return self.current_page * self.per_page_count
 
    def page_html(self):
        # total page <= 11
        if self.max_page_num <= self.max_pager_count:
            pager_start = 1
            pager_end = self.max_page_num
        # total page > 11
        else:
            # current page <= 5
            if self.current_page <= self.half_max_pager_count:
                pager_start = 1
                pager_end = self.max_pager_count
            else:
                # current page + 5 > total page
                if (self.current_page + self.half_max_pager_count) > self.max_page_num:
                    pager_end = self.max_page_num
                    pager_start = self.max_page_num - self.max_pager_count + 1   #倒这数11个
                else:
                    pager_start = self.current_page - self.half_max_pager_count
                    pager_end = self.current_page + self.half_max_pager_count
 
        page_html_list = []
        # {source:[2,], status:[2], gender:[2],consultant:[1],page:[1]}
        # first page
        self.params['page'] = 1
        first_page = '<li><a href="%s?%s">Main</a></li>'.decode("utf-8") % (self.base_url,urlencode(self.params),)
        page_html_list.append(first_page)
        # previous page
        self.params["page"] = self.current_page - 1
        if self.params["page"] < 1:
            pervious_page = '<li class="disabled"><a href="%s?%s" aria-label="Previous">Previous</span></a></li>'.decode("utf-8") % (self.base_url, urlencode(self.params))
        else:
            pervious_page = '<li><a href = "%s?%s" aria-label = "Previous" >previous</span></a></li>'.decode("utf-8") % ( self.base_url, urlencode(self.params))
        page_html_list.append(pervious_page)
        # page number in middle
        for i in range(pager_start, pager_end + 1):
            self.params['page'] = i
            if i == self.current_page:
                temp = '<li class="active"><a href="%s?%s">%s</a></li>' % (self.base_url,urlencode(self.params), i,)
            else:
                temp = '<li><a href="%s?%s">%s</a></li>' % (self.base_url,urlencode(self.params), i,)
            page_html_list.append(temp)
 
        # next page
        self.params["page"] = self.current_page + 1
        if self.params["page"] > self.max_page_num:
            self.params["page"] = self.current_page
            next_page = '<li class="disabled"><a href = "%s?%s" aria-label = "Next">Next</span></a></li >'.decode("utf-8") % (self.base_url, urlencode(self.params))
        else:
            next_page = '<li><a href = "%s?%s" aria-label = "Next">next</span></a></li>'.decode("utf-8") % (self.base_url, urlencode(self.params))
        page_html_list.append(next_page)
 
        # end page
        self.params['page'] = self.max_page_num
        last_page = '<li><a href="%s?%s">End</a></li>'.decode("utf-8") % (self.base_url, urlencode(self.params),)
        page_html_list.append(last_page)
 
        return ''.join(page_html_list)