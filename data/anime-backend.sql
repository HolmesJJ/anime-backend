-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 17, 2025 at 06:44 PM
-- Server version: 10.4.14-MariaDB
-- PHP Version: 7.4.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `anime-backend`
--
CREATE DATABASE IF NOT EXISTS `anime-backend` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `anime-backend`;

-- --------------------------------------------------------

--
-- Table structure for table `project`
--

CREATE TABLE `project` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `style_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `project`
--

INSERT INTO `project` (`id`, `name`, `description`, `style_id`) VALUES
(1, '凡人修仙传', '一介凡人韩立，机缘巧合踏入修仙之路。他凭借坚韧意志与冷静头脑，在凶险万分的修仙界中步步为营，从低阶小修士一路拼搏，突破重重难关，踏上长生大道。这是一部以理性修仙、奇遇与成长并重的仙侠经典之作。', 1),
(2, '亚当斯一家', '这是一个黑暗又充满幽默的家庭，亚当斯一家以其古怪、离经叛道的生活方式出名。每位家庭成员都有独特的癖好与超凡能力，处处透露出怪异的魅力与反传统的思维，带来别具一格的喜剧效果与家庭温情。', 2),
(3, '妖精森林的小不点', '在一个奇幻的妖精森林里，小不点是一位天真可爱的小精灵。她充满好奇心，每天与朋友们经历各种奇妙的冒险。画风温馨，故事富含自然哲理与成长主题，适合全年龄段阅读，令人心生温暖。', 3),
(4, '黑之契约者', '在神秘“地狱之门”开启后，一群拥有异能但需付出代价的契约者现身。主角黑，身为最强契约者之一，隐藏身份在阴影中完成任务。他的过去、情感与人性逐渐揭示，一场关于真相与牺牲的战斗悄然展开。', 4),
(5, '小恶魔', '小恶魔生活在地狱，却向往人类世界的阳光与自由。她偷偷溜到地面，展开一系列令人啼笑皆非的冒险。作品充满幽默与反差萌，描绘恶魔世界与人类社会的对比，也传递了关于自我认同与成长的思考。', 5),
(6, '暗黑破坏神', '在充满邪恶与黑暗力量的世界中，勇者们为抵抗地狱军团挺身而出。史诗级战斗、残酷世界观与深度剧情构成了这部动作奇幻作品。玩家或读者将直面恐惧与混沌，亲历英雄与恶魔之间的生死较量。', 6),
(7, '她不当女主很多年', '她曾是万人瞩目的女主角，如今退居幕后多年，却意外再次被命运推回聚光灯下。在面对曾经的爱情、对手与理想时，她逐渐找回自己，也重新定义了“女主”身份。这是一部关于成长与自我救赎的温情小说。', 7);

-- --------------------------------------------------------

--
-- Table structure for table `project_detail`
--

CREATE TABLE `project_detail` (
  `id` int(11) NOT NULL,
  `paragraph` text NOT NULL,
  `image_description` text DEFAULT NULL,
  `video_description` text DEFAULT NULL,
  `project_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `project_detail`
--

INSERT INTO `project_detail` (`id`, `paragraph`, `image_description`, `video_description`, `project_id`) VALUES
(1, '雨丝斜斜地织进后山的竹林，阿砚握着采药锄的手沁出冷汗。三天前在溪边捡到的那半朵风干山茶，此刻正静静躺在她袖袋里，花瓣边缘诡异的焦黑痕迹，像被火燎过的伤口。\r\n青苔覆盖的石阶湿滑难行，她扶着斑驳的竹节喘息，忽然听见细碎的脚步声从竹林深处传来。不是雨滴打在竹叶上的簌簌声，是布料摩擦的窸窣，混着若有若无的铃铛轻响。', '雨中竹林，薄雾弥漫，青苔覆盖的石阶斜斜向上，一位古风少女身穿素色衣裙，神情紧张，握着采药锄，站在湿滑石阶上。她的袖袋微微鼓起，藏着半朵焦黑山茶花。背景竹影婆娑，细雨穿林，远处传来模糊人影，衣袂轻响，伴随隐约的铃铛声。阴郁、神秘、东方幻想画风，写实风格，高细节，电影感光影。', '一位古风少女在雨中山林行走，身穿素色长裙，手握采药锄，神情紧张。她走在湿滑的青苔石阶上，不时扶着竹子喘息。袖袋中藏着一朵焦黑山茶花，镜头特写花瓣。四周竹林密布，雨丝斜织，雨滴敲打竹叶。忽然，远处传来脚步声和铃铛声，少女停下脚步，紧张回头。氛围紧张神秘，东方幻想风，电影质感，慢镜头切换，细雨动态粒子效果。', 1),
(2, '阿砚屏住呼吸，顺着声音拨开低垂的竹枝，雾气在眼前骤然散开。穿猩红嫁衣的少女正立在断碑前，嫁衣上金线绣的凤凰泛着冷光，发间凤冠垂落的珠翠在雨中摇晃。她苍白的指尖抚过碑上剥落的字迹，腕间银铃突然发出清越声响，惊起林间一群白鸟。阿砚后退半步，踩到枯枝的脆响惊动了少女，那双漆黑的眸子转过来时，她看见对方眼角点着朱砂痣，红得像凝固的血。', '竹林深处，薄雾弥漫，一位身穿猩红嫁衣的古风少女立于断裂的石碑前，嫁衣上金线绣出冷光闪烁的凤凰图案，凤冠垂珠随雨水微晃。她神情寂静，抚摸斑驳碑文，苍白的手指纤细而坚决，腕间银铃发出清越响声，林中一群白鸟飞起。远处，一位少女（阿砚）在竹林中屏息窥视，踩断一根枯枝，惊扰红衣女子，那人缓缓回头，眼角一枚朱砂痣鲜红如血，神秘惊艳。东方古典，写实风格，雨中雾气，电影级光影，暗红色调。', '细雨竹林中，一位少女（阿砚）拨开低垂竹枝，眼前雾气散开。镜头切换，一位身穿猩红嫁衣的古风女子站在断裂石碑前，嫁衣上的金线凤凰在雨中闪耀微光，凤冠垂珠在雨中轻晃。她苍白的手指轻抚碑文，腕间银铃突然清响，一群白鸟从林中飞起。阿砚惊退，脚下枯枝断裂发出清响。镜头缓慢推进，红衣少女回头，一双黑眸冷峻，眼角一点朱砂痣鲜红如血，氛围紧张诡谲，东方幻想电影风格，烟雨特效，慢镜头，情绪渲染。', 1),
(3, '“你见过阿照吗？” 少女的声音像浸在冰水里的丝线，嫁衣下摆不知何时已缠上了带刺的藤蔓，“那个说要带我出竹林的人。” 阿砚喉咙发紧，目光扫过断碑 —— 碑角残留的 “明永乐” 字样，与村里老人讲的百年前殉情新娘的传说渐渐重叠。\r\n雷声碾过天际，少女的嫁衣突然无风自动，藤蔓疯狂生长缠住她的脚踝。阿砚鬼使神差地伸手去拉，却只触到一片冰冷。少女的身影在雨幕中消散，唯有银铃坠地的脆响惊醒了她。低头时，自己掌心不知何时多了道血痕，形状竟与袖袋里那朵山茶的焦痕一模一样。', '古老竹林中，雷雨将至，一位穿着猩红嫁衣的少女立于断碑前，嫁衣无风自动，裙摆缠绕着疯长的带刺藤蔓。她眼神哀伤，仿佛在低声询问“你见过阿照吗？”。背景为剥蚀斑驳的断碑，隐约可见“明永乐”字样。空气中弥漫诡异气氛，少女身影开始在雨幕中消散，只留银铃坠地，脆响悠长。前景中，一位神情惊恐的古风少女（阿砚）低头看着掌心的血痕，血痕形状如焦黑山茶花花瓣。东方灵异幻想风格，雨夜氛围，电影级写实渲染，神秘、惊悚、情绪张力强。', '雷雨交加的竹林中，红衣古风少女站在断碑前，嫁衣无风自动，裙摆被带刺藤蔓缠绕。她轻声问：“你见过阿照吗？”声音冰冷哀怨。镜头特写石碑上模糊的“明永乐”字样，背景雷声滚滚。藤蔓疯狂生长缠住她脚踝，少女面容苍白，身影逐渐在雨幕中淡去。阿砚神情紧张，伸手去拉，却只触碰到冰冷空气。银铃坠地的清脆声响划破寂静，少女彻底消失。镜头俯视，阿砚掌心出现一道血痕，正与袖袋中那朵焦黑山茶花的痕迹一模一样。电影感剪辑，东方灵异惊悚风格，慢镜、雨幕粒子、雷电特效，高情绪张力。', 1),
(4, '雨停时，阿砚逃回村子。祠堂的族谱被她翻得哗哗作响，泛黄的纸页间，某页边角的小楷让她瞳孔骤缩：“永乐十五年，林氏女阿鸢与书生赵照私定终身，遭族中反对，相约私奔于竹林...” 字迹到此戛然而止，墨迹晕染得不成形状，像是被泪水浸透过。\r\n当夜，阿砚被银铃声惊醒。月光透过窗棂，猩红嫁衣的一角正从屋檐垂下，凤冠上的珍珠在黑暗中泛着幽光。“阿照说会带红山茶来接我...” 少女的声音贴着她耳畔响起，“可他再也没回来。” 阿砚颤抖着摸出那半朵山茶，花瓣突然在掌心化作齑粉，簌簌落在嫁衣的凤凰纹上。\r\n远处传来公鸡打鸣声，嫁衣瞬间消失。阿砚跌跌撞撞冲到后山，晨雾中的断碑前，新添了半朵带露的红山茶，与她昨夜散落的花瓣严丝合缝。竹叶间，银铃的余韵还在回荡，仿佛某个被遗忘的约定，终于在百年后等到了回音。', '古村祠堂内，少女阿砚翻阅发黄族谱，神色惊异，小楷文字写着“永乐十五年，林氏女阿鸢与赵照私定终身...”，纸页边缘泪痕晕墨。夜色中，阿砚在月光下惊醒，猩红嫁衣一角垂落于窗棂，凤冠珠翠在黑夜中发出幽幽冷光。一位模糊少女幻影贴近她耳语，声音哀怨：“阿照说会带红山茶来接我。” 阿砚掌心中半朵干山茶花化作粉末，洒落在嫁衣凤凰图案上。次日清晨，雾气弥漫的竹林断碑前，新添半朵带露红山茶，严丝合缝地拼合昨夜遗落之花。竹叶轻晃，银铃余音未散，氛围神秘、感伤、带宿命色彩。东方写意灵异风，高细节，情绪化构图，电影画幅。', '雨停，少女阿砚跌撞回村，画面切入昏暗祠堂，她翻动泛黄族谱，镜头特写“永乐十五年...林氏女阿鸢与书生赵照...” 墨迹被泪水晕染模糊。夜晚，她被银铃声惊醒，镜头缓慢推进窗边，一角猩红嫁衣从屋檐垂下，凤冠珠子在黑夜中闪着冷光。阿砚神情惊恐，幻影少女低声贴耳说：“阿照说会带红山茶来接我...” 阿砚掏出那半朵干山茶，花瓣忽然化为齑粉洒落在嫁衣上。鸡鸣声响起，嫁衣瞬间消失。清晨，阿砚奔向后山断碑前，雾气缭绕，一朵带露红山茶静静拼合昨夜遗落花瓣。镜头缓慢推远，竹叶轻晃，银铃回荡，仿佛百年前未完的承诺终于应验。电影质感，慢镜、光影切换、淡入淡出，东方幻想风。', 1);

-- --------------------------------------------------------

--
-- Table structure for table `style`
--

CREATE TABLE `style` (
  `id` int(11) NOT NULL,
  `style` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `style`
--

INSERT INTO `style` (`id`, `style`) VALUES
(1, '忘语'),
(2, '康拉德'),
(3, '㭴木祐人'),
(4, '冈村天斋'),
(5, '苍天血'),
(6, '萩原一至'),
(7, '蓝艾草');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `project`
--
ALTER TABLE `project`
  ADD PRIMARY KEY (`id`),
  ADD KEY `style_id` (`style_id`);

--
-- Indexes for table `project_detail`
--
ALTER TABLE `project_detail`
  ADD PRIMARY KEY (`id`),
  ADD KEY `project_id` (`project_id`);

--
-- Indexes for table `style`
--
ALTER TABLE `style`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `project`
--
ALTER TABLE `project`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `project_detail`
--
ALTER TABLE `project_detail`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `style`
--
ALTER TABLE `style`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `project`
--
ALTER TABLE `project`
  ADD CONSTRAINT `project_ibfk_1` FOREIGN KEY (`style_id`) REFERENCES `style` (`id`);

--
-- Constraints for table `project_detail`
--
ALTER TABLE `project_detail`
  ADD CONSTRAINT `project_detail_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
