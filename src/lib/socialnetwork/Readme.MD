用户社交影响力 Cha 等[12]从转发次数、被提及次数以及关注者研究指出，微博用户粉丝的数量与微博被转发的次数及被提及的次数并没有简单的正相关关系，要刻画用户的影响力并不能仅仅通过粉丝数量。 Weng等[13]提出同质现象来解释用户之间相互关注的行为，并基于PageRank[14] 算法提出了对Twitter用户排名的TwitterRank算法，用来刻画Twitter用户的影响力。 YanChao-Zhang等[15]研究指出，新浪微博用户的粉丝数服从幂律分布。用户的影响力主要通过其转发微博和被提及的影响力来体现，而与粉丝数量没有很直接的关系。提出联合用户粉丝数量与社交网络规模的用户影响力模型，并通过实验验证该模型能很好地反映用户的影响力。
社交网络结构的分析 Kwak等[19]，Backstrom等[20]，Gonza´lez[21]，Mislove等[22]都得到了关于各自社交网络结构的特性，如社交关系中的幂律分布、社交行为形成小网络的小世界特性以及社交网络图结构无标度等特性。 Leskovec等[23]研究社交网络的网络结构社区模块性。在很小尺度的网络上观察到了紧密但是几乎微不足道的社区结构，然而在更大规模的网络上，最佳社区逐渐融入网络内社区外的部分中，反而不那么“社区化”了。
社交网络传播能力的分析 Leskovec 等[24]经做了关于社交网络用户如何传播病毒信息的研究，Jansen等提出了Twitter 上电子式“ 口口相传”（Word-of-Mouth, WoM）信息传播的传播模式[25]，传播范围也不会太广，传播速度也比较慢，在每一跳上都会有比较明显的延时。积极增长模式（Photo A）、缓慢增长模式（Photo C）以及激增模式（Photo B、D）。 Kwak等[19]Twitter用户对Twitter微博内容传播的影响一定程度上可以决定微博内容的流行度。 Kempe等[11]提出了社交网络的点度中心性和距离中心性等是决定社交网络影响力的关键因素。提出了启发式算法来利用各因素间的关系最大化影响力。 Zhang等[27]专家发现现象[28] Dodds等[29]认为社交网络中信息的传播就像现实中的传染病那样，社交网络用户可以被感染、免疫甚至治愈等。 Hartline等[30]充分利用了最大化的社交网络影响力，利用贪心算法最大化用户购买力。
用户分析 普通电视节目相关微博用户的年龄分布，一个有长尾的正态分布 top-10参与度PI（Participation Index）为：以用户数排名在第十的省份（含直辖市）为参照，其他省份相对于该省份的用户差距比例。公式如下：
其中，UNi代表省份i的微博用户数。 K-means算法在进行用户偏好分析之前，我们先简要介绍下用于聚类分析的K-means算法[66–68]。K-means是最常用的聚类分析方法，它的目的是把n 个点划分到k个聚类中，使得每个点都属于离它最近的聚类中心对应的类中。它能使得同一类中的点之间的距离尽可能的小，而类间点的距离尽可能的大。 假设有集合{x1; x2; : : : ; xn}，且其中每个元素都是一个d维矢量，k-means聚类就是在给定k(k ≤ n)值的情况下，把集合中的元素划分到k个集合S 1; S 2; : : : ; S k中，并使得组内平方和(WCSS)最小。也即，找到满足下式的收敛值：
其中，i是聚类S i中所有点的平均值。 其流程就是，在随机初始化了k个聚类中心m(1)1 ;m(1)2 ; : : : ;m(1)k 后，算法交替执行分配和更新，直至收敛。其中，分配过程是把每一个待测点分配到离它最近的聚类中心对应的聚类中。这个距离用欧氏距离来衡量○1 。
这样的分配使得在第t次分配后，每一个xp都被分配到一个确定的S (t)i 中。而在每次分配过后的更新就是指重新计算聚类中心，并用于下一次分配。计算聚类中心的公式为：
算法1描述了该聚类过程。我们将把它应用于我们的用户偏好分析中。
大多数用户都有一定的兴趣偏好，他们并不总是兴趣广泛。接下来，对用户的带权标签向量进行归一化后，我们便可以计算任意两个用户之间的“ 距离”。然后，我们根据标签距离，利用k-means 聚类算法[66] 对这些用户进行聚类。我们设置聚类类别k = 30，即把我们的用户根据标签聚成30类。
他们形成的社交网络有一个相当大的聚类系数[69]用户之间紧密联系在一起。这也说明，他们本身在社交上的聚集情况与兴趣聚集情况非常相符。 一个网络的平均聚类系数（ACC）反映的是网络节点聚类或抱团的总体迹象，也即节点的紧密程度。当ACC为0时，网络中的每个节点都是孤立的，与其他节点毫无联系；而ACC 为1 的网络则是全连通的。而聚类系数和平均最短路径（ASP）一起，能够展示所谓的“小世界”效应，表明节点如何嵌入其邻居节点当中。 根据Watts-Strogatz 模型理论[70]，他们形成的社交网络接近于小世界网络。从交互型用户的社交好友入手进行推广会收到较好的效果。 该类中有一些比较特殊的节点——机构账号，如腾讯视频、湖南卫视、腾讯娱乐等。聚到该类中的用户，他们本身之间没有或几乎没有联系，仅仅是共同关注了这些机构账号。相比于图5.4(a)中的网络结构，这样的网络平均聚类系数相对较小（ACC = 0:305），平均最短路径相对大点（ASP = 1:63），图密度也很小。他们可以从这些机构账号的粉丝中发掘电视节目的潜在观众。
微博与票房 [3]通过电影首映前一周微博的量化表现来预测电影首映的票房。 [16]通过用户微博被转发的情况以及用户自身在微博中的消极性来计算影响力，并且在在线视频网站的点击量试验中取得了较好的效果。 江雪*提出了基于用户固有影响力和交互影响力的NMR算法，对电视节目微博用户在微博的影响力做评价。 跨平台收视率预测。选择最具相关性的属性来描述不同信息，利用决策树构建基于微博的收视率模型，对收视率进行预测。
用户行为分析 发微博时间特性
微博被转发时间特性
小世界网络：平均路径长度短，聚类系数较高
利用Influence Passive算法，对基于电视节目的相关微博用户展开实验。
微博信息与收视信息相关性
微博量与电视收视是正相关的，Spearman相关系数是0,843.
社交关系与收视关系 聚类系数 0.402 平均路径长度 0.839 平均度 0.607
影响力与收视关系 IP 0.645 NMR 0.647
Quinlan的ID3决策树算法。
社交媒体与收视率/票房 A和H[41]对电影首映前一周与电影相关微博的量化表现来预测电影首映的票房。 江雪【2】对同地区同时间段收视数据进行研究，微博量与电视收视是正相关的。 Mishne 和Glance【1】对情感因素和电影票房的关系进行研究，发现无论是电影首映之前还是之后，微博评论和电影票房有很好的相关性。简单地利用情感分析能提高这些相关性。而且在影片的预映阶段，正面评价的数量比单纯的微博评论数更相关。 林霞虹【4】利用社交数据对影视媒体的分析，从关联性分析和预测分析两方面都有较为成熟的研究工作。现有工作针对的影视媒体几乎都为电影。 惠普实验室的Asur等[41]用之前7天的历史数据线性拟合预测票房，取得较高的准确率。而Delen等[42]则用信息融合方法预测好莱坞电影票房，Sharda等[43]根据微博正负面情感的比例用神经网络预测是否会有较好票房收视，Mishne等[44]则通过分析发现，微博数量加上微博情感的收视率预测准确率比单纯用微博数量的预测要高。 林霞虹【4】微博情感比例比较极端（较多的正面或负面情感微博）的电视节目收视率相对反而较低。 林霞虹【4】演员为非微博关注或好友关系的其他演员的作品发微博做推广，这样的行为是很常见的。 积累分布函数：能完整描述一个实数随机变量X的概率分布，是概率密度函数的计分。 反例：Wong等[45]用IMDb○1 和烂番茄 ○2 上的评分作为电影收视的参考，发现Twitter上的正面评价高并不总能导致收视高，反之也一样。
我们整理出关于所有65部电视节目的25个标签，如偶像、现代、战争、家庭、古装、言情等。对于每一个微博用户，根据他们所发的微博，我们可以给他们分配一个类型标签的权重向量。这个权重是根据他们所发的特定类别的电视节目的微博 数累加的。如电视节目v1的类型标签是爱情、偶像、言情，而某微博用户发了关于v1的3条微博，则对应的在他的标签向量的爱情、偶像、言情维上分别加上3。在得到所有用户的标签向量后，我们先对用户的标签数目做一个统计。
内容分析 情感分析在语言学和机器学习中被广泛研究，在早期的工作中已经有不少的分类模型[71]。 我们可以把它们分为“带正面情感（积极）”、“带负面情感（消极）”和“不带情感（中性）”三类。
明星的价值 Ravid’s (1999) measures directly relate to the two kinds of reputations that can generally be the source of stars’ power: an economic reputation, derived from their box office success, and an artistic reputation, derived from the recognition of critics or peers (Delmestri, Montanari and Usai 2005). A star’s historical box office record has been found to be an indicator of his future potential in some studies (e.g., Litman and Kohl 1989, Sochay 1994, Ravid 1999, Lampel and Shamsie 2003)1, and is a valued source of information for studio executives (Chisholm 2004). A star’s artistic reputation, which in the motion picture industry is primarily revealed by means of awards or nominations, is a sign of quality for audiences, executives, the media, and other constituencies (e.g., Wallace et al 1993), and thus also a likely predictor of that star’s future box office record. StarBond values in December 2001 are only weakly correlated with such values exactly three years later—the Pearson correlation coefficient is 0.43
票房预测方法 The majority of extant studies considers a measure of talent involvement as one of the independent variables, and box office revenues or profits as the dependent variable, either in a regression model (e.g. Austin 1989; Litman 1983;Litman and Kohl 1989; Prag and Casavant 1994; Sochay 1994; Litman and Ahn 1998; Wallace et al 1993; Ravid 1999; Elberse and Eliashberg 2003) or a probability model (e.g. Sawhney and Eliashberg 1996; De Vany and Walls 1999; Neelamegham and Chintagunta 1999).
关联性分析 林霞虹【4】，用Zipf-like模型刻画电视节目流行度的效果有显著提升，然而效果并不是最理想的。而广延模型不仅在刻画流行度上很准确，而且它不受数据集本身倾斜或是噪声的影响，能始终保持在较高水平的拟合优度上。
流行度分析 Cha等[4]分析了基于用户生成内容（User Generated Content, UGC）视频点播系统下视频的流行度以及访问模式等。他们对YouTube 、Netflix 、Yahoo!和Daum等大型视频网站上的典型视频进行分析，发现了流行度分布的长尾现象，并提出刻画流行度的模型。 Avramova等[5]则分析了YouTube等多个视频生成系统的视频流行度随时间演变过程。他们提出了一个可以退化成幂律分布或者指数分布的模型。
[1] G. Mishne and N. Glance. Predicting movie sales from blogger sentiment.In AAAI 2006 Spring Symposium on Computational Approaches [2] 江雪，面向电视节目的微博用户行为与特性分析，2013 [4] 林霞虹，联合社交属性与流行度的电视节目关注度分析 [41] Asur S, Huberman B A. Predicting the future with social media. Proceedings of Web Intelligence and Intelligent Agent Technology (WI-IAT), 2010 IEEE/WIC/ACM International Conference on, volume 1. IEEE, 2010. 492–499. [42] Delen D, Sharda R. Predicting the Financial Success of Hollywood Movies Using an Information Fusion Approach. Industrial Engineering Journal, 2010, 21(1):30–37. [43] Sharda R, Delen D. Predicting box-oce success of motion pictures with neural networks. Expert Systems with Applications, 2006, 30(2):243–254. [44] Mishne G, Glance N S. Predicting Movie Sales from Blogger Sentiment. Proceedings of AAAI Spring Symposium: Computational Approaches to Analyzing Weblogs, 2006. 155–158. [45] Wong F M F, Sen S, Chiang M. Why watching movie tweets won’t tell the whole story? Proceedings of Proceedings of the 2012 ACM workshop on Workshop on online social networks. ACM, 2012. 61–66.
粉丝数幂律分布 小世界网络：平均路径长度短，聚类系数较高
1.明星行为分析 a.发微博时间 a`.转发微博时间
b.发微博数量 c.转发数量
c发帖文字长度
c发帖emoji表情
c``发帖语气词
d.收到评论数量 e.收到赞数量 f.粉丝数量
g.提及数量
2.一度好友分析（定义为一度好友） g.一度好友数量 h.一度好友平均粉丝数量 i.一度好友平均博龄 j.一度好友男女比例 k.一度好友平均发微博数量
l.互粉数量