'''
功能：生成页标的工具类
输入：   :param url: 路由地址，eg：/blog/
        :param record_sum: 记录总数
        :param current_page: 当前查询页
        :param max_pages: 窗口显示的最多页标数，默认11
        :param max_records: 每页的最大记录数，默认10
输出： 安全的页码a标签 eg: <a href ="/resmanage/?page=1">1</a>

eg:
视图函数：
def host(request):
    from login.utils.pagination import Pageination

    queryResult=models.ResManage.objects.all()

    pagedict={}
    # request.path_info 可获取当前url的路径，如/host/?page=1的path_url=/host/
    pagedict["url"]=request.path_info
    pagedict["record_sum"]=queryResult.count()
    pagedict["current_page"]=request.GET.get("page")
    pagedict["max_pages"]=11     # 默认11，可不传入
    pagedict["max_records"]=10   # 默认10，可不传入

    page_obj=Pageination(**pagedict)
    res_obj=queryResult[page_obj.start:page_obj.end]

    return render(request,"resmanage.html",{"html":page_obj.page()})
    ###################################################################
    # 这里一定要注意的是 res_obj 需要取代原来的查询结果集，如原来写成的 #
    #  result=models.Strudent.objects.all() 则需要替换成              #
    #  result=queryResult[page_obj.start:page_obj.end]               #
    ##################################################################
html:
    <!--页码标签-->
    <style>
        .page a{
            display: inline-block;
            padding: 1px 5px;
            margin: 0px 3px;
            border: 1px solid darkgrey;
            text-align: center;
        }
        .active{
            background-color: cornflowerblue;
        }
    </style>

    <div class="page">{{ html }}</div>
'''


from django.utils.safestring import mark_safe

class Pageination(object):

    def __init__(self,url,record_sum,current_page,max_pages=11,max_records=10):
        '''

        :param url: 路由地址，eg：/blog/
        :param record_sum: 记录总数
        :param current_page: 当前查询页
        :param max_pages: 窗口显示的最多页标数，默认11
        :param max_records: 每页的最大记录数，默认10
        '''

        # 输入的页码不对则返回第一页
        self.url=url
        try:
            self.current_page=int(current_page)
        except Exception:
            self.current_page=1

        self.record_sum=record_sum
        self.max_pages=int(max_pages)
        self.max_records=int(max_records)
        self.page_num, self.last_page_count = divmod(self.record_sum, self.max_records)  # 分页数，最后一页的记录数
        self.half_max_pages=int(self.max_pages/2)

        if self.last_page_count: # 如果最后一页存在记录，则总页数+1
            self.page_num+=1
        if self.current_page> self.page_num or self.current_page<1: # 如果输入的页码不在正常范围，则页码为1
            self.current_page=1


    # start 和 end 作为数据切片用，返回起始行和结束行
    @property
    def start(self):
        return (self.current_page-1)*self.max_records

    @property
    def end(self):
        return self.current_page*self.max_records

    # 普通页面返回
    def page(self):

        # 如果分页数比设置的最大显示分页数小（默认11），那么就按照实际分页数显示； 否则 按照当前页前5个+当前页+后五个 总共显示11页
        if self.page_num <= self.max_pages:
            page_start = 1
            page_end = self.page_num+1
        else:
            page_start = self.current_page - self.half_max_pages
            page_end = self.current_page + self.half_max_pages + 1

            if page_start <= 1:
                page_start = 1
                page_end = self.max_pages + 1
            if page_end >= self.page_num:
                page_start = self.page_num - self.max_pages
                page_end = self.page_num + 1

        s = []

        # 添加 首页 上下页 尾页 常用页面
        s.append('<a href ="%s?page=%s">首页</a>' % (self.url, 1))
        if self.current_page <= 1:
            pre_current_page = self.current_page
        else:
            pre_current_page = self.current_page - 1
        s.append('<a href ="%s?page=%s">上一页</a>' % (self.url, pre_current_page))

        for i in range(page_start, page_end):
            if i == self.current_page:
                s.append('<a href ="%s?page=%s" class="active">%s</a>' % (self.url, i, i))
            else:
                s.append('<a href ="%s?page=%s">%s</a>' % (self.url, i, i))

        if self.current_page == self.page_num:
            nex_current_page = self.page_num
        else:
            nex_current_page = self.current_page + 1

        s.append('<a href ="%s?page=%s">下一页</a>' % (self.url, nex_current_page))
        s.append('<a href ="%s?page=%s">尾页</a>' % (self.url, self.page_num))


        html = "".join(s)

        return  mark_safe(html)


    # 套用bootstrap页面返回
    def bootstrap_page(self):
        '''
        套用的话，在html里还得加上：
        <nav aria-label="Page navigation">
        <ul class="pagination">
                {{ html }}
        </ul>
        </nav>
        '''

        # 如果分页数比设置的最大显示分页数小（默认11），那么就按照实际分页数显示； 否则 按照当前页前5个+当前页+后五个 总共显示11页
        if self.page_num <= self.max_pages:
            page_start = 1
            page_end = self.page_num+1
        else:
            page_start = self.current_page - self.half_max_pages
            page_end = self.current_page + self.half_max_pages + 1

            if page_start <= 1:
                page_start = 1
                page_end = self.max_pages + 1
            if page_end >= self.page_num:
                page_start = self.page_num - self.max_pages
                page_end = self.page_num + 1

        s = []

        # 添加 首页 上下页 尾页 常用页面
        s.append(' <li><a href ="%s?page=%s">首页</a></li>' % (self.url, 1))
        if self.current_page <= 1:
            pre_current_page = self.current_page
        else:
            pre_current_page = self.current_page - 1
        s.append(' <li><a href ="%s?page=%s">上一页</a></li>' % (self.url, pre_current_page))

        for i in range(page_start, page_end):
            if i == self.current_page:
                s.append(' <li class="active"><a href ="%s?page=%s">%s</a></li>' % (self.url, i, i))
            else:
                s.append(' <li><a href ="%s?page=%s">%s</a></li>' % (self.url, i, i))

        if self.current_page == self.page_num:
            nex_current_page = self.page_num
        else:
            nex_current_page = self.current_page + 1

        s.append(' <li><a href ="%s?page=%s">下一页</a></li>' % (self.url, nex_current_page))
        s.append(' <li><a href ="%s?page=%s">尾页</a></li>' % (self.url, self.page_num))


        html = "".join(s)

        return  mark_safe(html)

