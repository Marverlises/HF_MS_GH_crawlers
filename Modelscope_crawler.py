# -*- coding: utf-8 -*-
# @Time       : 2024/11/21 9:04
# @Author     : Marverlises
# @File       : Modelscope_crawler.py
# @Description: 爬取Modelscope数据集信息
import json
import os
import logging
import time
import tqdm
from utils import extract_arxiv_link, extract_pdf_link, read_json_file, init_driver, parse_string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ModelscopeCrawler:
    def __init__(self, sort_method='downloads', headless=True, base_save_path='./result/modelscope',
                 target_json_path='./organization_links/model_scope_organization_links.json', log_level=logging.INFO,
                 organization_datasets_links_save_file='organization_datasets_links.json'):
        sort_method_map = {'synthesis': "综合排序", 'downloads': "下载量排序", 'likes': "收藏量排序",
                           'updated': "最近更新"}
        self.chosen_sort_method = sort_method_map[sort_method]
        self.driver = init_driver(headless=headless)
        self.screen_shot_save_path = base_save_path + '/modelscope_dataset_info_screenshots'
        self.crawl_targets = read_json_file(target_json_path)
        self.organization_datasets_links_save_file = base_save_path + '/' + organization_datasets_links_save_file
        self._init_logger(log_level=log_level)
        self._init_relevant_element_xpath()
        if os.path.exists(self.screen_shot_save_path) is False:
            os.makedirs(self.screen_shot_save_path)

    def _init_logger(self, log_level: int = logging.INFO) -> None:
        """
        初始化日志
        :return:
        """
        log_dir = './logs/MS'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, 'MS_crawl_log.log')
        logging.basicConfig(level=log_level,
                            format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                            handlers=[
                                logging.FileHandler(log_file),  # 写入文件
                                logging.StreamHandler()  # 控制台输出
                            ])
        logging.info("Start crawling MS dataset info")

    def _init_relevant_element_xpath(self) -> None:
        """
        初始化相关元素的Xpath
        :return:
        """
        # ================================= get_dataset_links相关元素的Xpath =================================
        # 所有数据集元素div
        self.dataset_elements_xpath = '//*[@id="normal_tab_dataset"]/div/div[3]/div/div/div/div[1]/div'
        # 数据集链接
        self.dataset_link_xpath = '//*[@id="organization_rightContent"]/div/div/div[1]/div/div[4]'
        # 开始选择排序方式
        self.sort_method_xpath = '//*[@id="normal_tab_dataset"]/div/div[2]/div[2]/div/span[2]'
        # 排序方式的Xpath
        self.sort_xpath = f"//div[text()='{self.chosen_sort_method}']"
        # 下一页
        self.next_page_xpath = '//*[@id="normal_tab_dataset"]/div/div[3]/div/div/div/div[2]/ul/li[last()-1]'
        # 总页数
        self.total_page_xpath = '//*[@id="normal_tab_dataset"]/div/div[3]/div/div/div/div[2]/ul/li[last()-2]'
        # ================================= get_dataset_info相关元素的Xpath =================================
        # 开源协议
        self.dataset_license_xpath = '//*[@id="root"]/div/div/main/div[1]/div[1]/div[1]/div/div/div[2]/div/div/span'
        # 相关信息
        self.related_info_xpath = '//*[@id="root"]/div/div/main/div[1]/div[1]/div[1]/div/div/div[3]/div[1]'
        # introduction
        self.introduction_xpath = '//*[@id="modelDetail_bottom"]/div/div[1]'
        # community activities
        self.community_activities_xpath = '//*[@id="modelDetail_bottom"]/div/div/div[2]/div[1]/div'

    def get_dataset_links(self):
        """
        获取机构发布的数据集链接
        :return:    机构发布的数据集链接
        """
        organization_datasets_links = {}
        # 遍历所有机构链接，获取机构发布数据集链接
        for index, target in self.crawl_targets.items():
            try:
                if target is None or target == '':
                    continue
                logging.info(f"Start crawling {index} datasets")
                self.driver.get(target)
                # 进入数据集页面
                time.sleep(5)
                self.driver.find_element(By.XPATH, self.dataset_link_xpath).click()
                # 排序方式
                time.sleep(3)
                self.driver.find_element(By.XPATH, self.sort_method_xpath).click()
                # 选择排序方式
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, self.sort_xpath))
                    ).click()
                except:
                    raise Exception(f"Can't find sort method: {self.chosen_sort_method}")

                # 等待页面全部加载完成
                time.sleep(3)
                dataset_elements = self.driver.find_elements(By.XPATH, self.dataset_elements_xpath)
                # 获取当前页面的所有数据集链接
                logging.info(f"Current page has {len(dataset_elements)} datasets")
                if not dataset_elements or len(dataset_elements) == 0 or any(
                        "无数据集" in element.text for element in dataset_elements):
                    logging.info(f"No dataset found for {index}")
                    continue
                # 爬取首页数据
                dataset_links, dataset_last_update_time, dataset_download_num, dataset_like_num = self._get_page_info(
                    dataset_elements)
                if index not in organization_datasets_links:
                    organization_datasets_links[index] = {
                        "dataset_links": dataset_links,
                        "dataset_last_update_time": dataset_last_update_time,
                        "dataset_download_num": dataset_download_num,
                        "dataset_like_num": dataset_like_num
                    }
                else:
                    organization_datasets_links[index]["dataset_links"].extend(dataset_links)
                    organization_datasets_links[index]["dataset_last_update_time"].extend(dataset_last_update_time)
                    organization_datasets_links[index]["dataset_download_num"].extend(dataset_download_num)
                    organization_datasets_links[index]["dataset_like_num"].extend(dataset_like_num)

                # 多页情况的处理
                try:
                    WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="normal_tab_dataset"]/div/div[3]/div/div/div/div[2]/ul')))
                except:
                    logging.info("Only one page")
                    logging.info(f"Finish crawling {index} datasets")
                    continue
                self._iterate_other_pages(index, organization_datasets_links)
            except Exception as e:
                logging.error(f"Error: {e}, when crawling page {index} dataset")
                raise e

        logging.info(f"Finish crawling all datasets")
        # 保存数据集链接
        with open(self.organization_datasets_links_save_file, 'w', encoding='utf-8') as f:
            json.dump(organization_datasets_links, f, ensure_ascii=False)
        return organization_datasets_links

    def _iterate_other_pages(self, index, organization_datasets_links):
        """
        遍历其余页面中数据集的信息
        :param index:                       当前机构的索引
        :param organization_datasets_links: 结果集
        :return:                            None
        """
        # 获取总页数
        total_page = self.driver.find_element(By.XPATH, self.total_page_xpath).get_attribute('title')
        logging.info(f"Total page: {total_page}")
        # 遍历所有页
        for page in range(2, int(total_page) + 1):
            try:
                self.driver.find_element(By.XPATH, self.next_page_xpath).click()
                time.sleep(3)
                # 获取当前页面的所有数据集链接
                dataset_elements = self.driver.find_elements(By.XPATH, self.dataset_elements_xpath)
                logging.info(f"current page datasets have: {len(dataset_elements)}")

                dataset_links, dataset_last_update_time, dataset_download_num, dataset_like_num = self._get_page_info(
                    dataset_elements)

                organization_datasets_links[index]["dataset_links"].extend(dataset_links)
                organization_datasets_links[index]["dataset_last_update_time"].extend(dataset_last_update_time)
                organization_datasets_links[index]["dataset_download_num"].extend(dataset_download_num)
                organization_datasets_links[index]["dataset_like_num"].extend(dataset_like_num)
            except Exception as e:
                logging.error(f"Error: {e}, when crawling page {page} dataset, current index: {index}")

    def _get_page_info(self, dataset_elements):
        """
        获取当前页面的数据集信息
        :param dataset_elements:    当前页面的数据集元素
        :return:                    数据集链接、最后更新时间、下载量、收藏量
        """
        dataset_links = [element.find_element(By.TAG_NAME, 'a').get_attribute('href') for
                         element in dataset_elements]
        dataset_last_update_time = [element.find_element(By.XPATH, 'a/div/div[2]/div[2]/div[1]').text for
                                    element in dataset_elements]
        dataset_download_num = [element.find_element(By.XPATH, 'a/div/div[2]/div[2]/div[2]').text for
                                element in dataset_elements]
        dataset_like_num = [element.find_element(By.XPATH, 'a/div/div[2]/div[2]/div[3]').text for
                            element in dataset_elements]
        assert len(dataset_elements) == len(dataset_links) == len(dataset_last_update_time) == len(
            dataset_download_num) == len(dataset_like_num)
        logging.info(f"dataset_links: {dataset_links}")
        return dataset_links, dataset_last_update_time, dataset_download_num, dataset_like_num

    def preprocess_dataset_info(self):
        """
        预处理数据集信息——获取所有数据集的链接
        :return:
        """
        # 首先查看是否爬取了数据集链接
        if not os.path.exists(self.organization_datasets_links_save_file):
            self.get_dataset_links()
        # 读取数据集链接
        targets = read_json_file(self.organization_datasets_links_save_file)
        all_dataset_links = []
        all_dataset_download_num = []
        all_dataset_like_num = []
        all_dataset_last_update_time = []
        # 获取所有数据集的链接
        for organization, info in targets.items():
            all_dataset_links.extend(info['dataset_links'])
            all_dataset_download_num.extend(info['dataset_download_num'])
            all_dataset_like_num.extend(info['dataset_like_num'])
            all_dataset_last_update_time.extend(info['dataset_last_update_time'])
        logging.info(f"Total dataset: {len(all_dataset_links)}")
        assert len(all_dataset_links) == len(all_dataset_download_num) == len(all_dataset_like_num) == len(
            all_dataset_last_update_time)
        return all_dataset_links, all_dataset_download_num, all_dataset_like_num, all_dataset_last_update_time

    def crawl_dataset_info(self):
        """
        获取所有数据集的详细信息
        :return:                                {组织名：{数据集名：{详细信息}}}，异常链接
        """
        # 获取所有数据集的链接以及下载量、收藏量、最后更新时间
        all_dataset_links, all_dataset_download_num, all_dataset_like_num, all_dataset_last_update_time = self.preprocess_dataset_info()
        # 结果集
        dataset_details = {}
        exception_links = []
        # 遍历所有数据集链接
        for i in tqdm.tqdm(range(len(all_dataset_links))):
            link = all_dataset_links[i]
            try:
                self.driver.get(link)
                time.sleep(4)
                download_num = all_dataset_download_num[i]
                like_num = all_dataset_like_num[i]
                last_update_time = all_dataset_last_update_time[i].split(" ")[0]
                organization = link.split("/")[-2]
                dataset_name = link.split("/")[-1]
                logging.info(f"正在获取数据集详细信息：{link}")
                # 首先对当前页面进行截图，保存到model_scope_dataset_info_screenshots文件夹下
                self.driver.save_screenshot(f"{self.screen_shot_save_path}/{dataset_name}.png")
                # 获取开源协议，下载量，介绍面板显示数据集大小（不一定有用，很多和实际大小有很大差异）,以及整个介绍面板的内容
                dataset_license = self.driver.find_element(By.XPATH, self.dataset_license_xpath).text
                if "开源协议：" in dataset_license:
                    dataset_license = dataset_license.replace("开源协议：", "")
                related_info = self.driver.find_element(By.XPATH, self.related_info_xpath).text
                related_info = parse_string(related_info)
                introduction = self.driver.find_element(By.XPATH, self.introduction_xpath).text
                # 从introduction中提取相关论文链接
                arxiv_pdf_link = extract_arxiv_link(introduction)
                only_pdf_link = extract_pdf_link(introduction)
                # 进入feedback页面，获取社区活跃度
                self.driver.get(link + '/feedback')
                time.sleep(1)
                community_activities = self.driver.find_element(By.XPATH, self.community_activities_xpath).text
                # 获取pdf的截图
                if arxiv_pdf_link:
                    self.get_pdf_screenshots(arxiv_pdf_link, dataset_name)
                elif only_pdf_link:
                    self.get_pdf_screenshots(only_pdf_link, dataset_name)
                else:
                    logging.info("没有pdf链接")

                dataset_details.setdefault(organization, {})[dataset_name] = {"dataset_license": dataset_license,
                                                                              "related_info": related_info,
                                                                              "introduction": introduction,
                                                                              "community_activities": community_activities,
                                                                              "dataset_screenshot_save_path": f"result/modelscope/model_scope_dataset_info_screenshots/{dataset_name}.png",
                                                                              "paper_screenshot_save_path": f"result/modelscope/model_scope_dataset_info_screenshots/{dataset_name}_pdf.png" if arxiv_pdf_link or only_pdf_link else '',
                                                                              "download_num": download_num,
                                                                              "like_num": like_num,
                                                                              "last_update_time": last_update_time,
                                                                              "link": link}

                logging.info(f"Got dataset: {link}, dataset name: {dataset_name}")
            except:
                exception_links.append(link)
                logging.error(f"Error when crawling page dataset {i}")
                continue
        return dataset_details, exception_links

    def get_pdf_screenshots(self, pdf_link, dataset_name):
        """
        获取pdf的截图
        :param pdf_link:        pdf链接
        :param dataset_name:    数据集名
        :return:                None
        """
        if pdf_link:
            logging.info(f"正在获取pdf截图：{pdf_link}")
            self.driver.get(pdf_link)
            time.sleep(8)
            self.driver.save_screenshot(
                f"{self.screen_shot_save_path}/{dataset_name}_pdf.png")


if __name__ == '__main__':
    modelscope_crawler = ModelscopeCrawler(headless=False)
    # data = modelscope_crawler.get_dataset_links()
    dataset_details, exception_links = modelscope_crawler.crawl_dataset_info()
    # save
    with open('./result/modelscope/dataset_details.json', 'w', encoding='utf-8') as f:
        json.dump(dataset_details, f, ensure_ascii=False)
    with open('./result/modelscope/exception_links.json', 'w', encoding='utf-8') as f:
        json.dump(exception_links, f, ensure_ascii=False)

    print("Finish")
