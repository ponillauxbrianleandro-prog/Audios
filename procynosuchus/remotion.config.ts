import { Config } from '@remotion/cli/config';
Config.setBrowserExecutable('/opt/pw-browsers/chromium');
Config.setChromeMode('chrome-for-testing');
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setConcurrency(4);
