import unittest
import sys
import os

# Find modules from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.ingestion import categorize_video

class TestGTMDataPipeline(unittest.TestCase):

    def test_ai_categorization(self):
        """Ensure titles with AI keywords route to the correct topic and format."""
        title = "How To Use ChatGPT For Extreme Inbound Scale"
        topic, video_format = categorize_video(title)

        self.assertEqual(topic, "AI & Automation")
        self.assertEqual(video_format, "Product Tutorial")

    def test_gtm_strategy_case_study(self):
        """Ensure marketing and case study keywords are isolated correctly."""
        title = "The Story Behind Why I Changed Our Sales Structure"
        topic, video_format = categorize_video(title)

        self.assertEqual(topic, "GTM Strategy")
        self.assertEqual(video_format, "Founder Case Study")

    def test_fallback_graceful_handling(self):
        """Ensure non-matching titles drop into the standard fallback categories without failing."""
        title = "Random Vlog Talking About Life At The Office"
        topic, video_format = categorize_video(title)

        self.assertEqual(topic, "General Business")
        self.assertEqual(video_format, "Standard Content")


if __name__ == '__main__':
    unittest.main()