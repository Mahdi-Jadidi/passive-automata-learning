"""Exact fixed-partition decision from finite projected positive languages."""


class ProjectionTeacher:
    """Consume aligned projected samples of an already validated partition."""

    def __init__(self, tick):
        self.tick = tick
        self.stats = {}

    def check(self, blocks, images):
        self.stats = {'dfa_representations': 0, 'blocks_checked': 0,
                      'positive_rows': 0, 'negative_membership_tests': 0}
        self.tick()
        negative_count = len(images[blocks[0]]['negative']) if blocks else 0
        if any(len(images[block]['negative']) != negative_count for block in blocks):
            raise ValueError('negative projection lists must have equal length')
        uncovered = list(range(negative_count))
        for block in blocks:
            if not uncovered:
                break
            image = images[block]
            positives = set()
            for word in image['positive']:
                self.tick()
                positives.add(word)
            still_uncovered = []
            for i in uncovered:
                self.tick()
                if image['negative'][i] in positives:
                    still_uncovered.append(i)
            self.stats['blocks_checked'] += 1
            self.stats['positive_rows'] += len(image['positive'])
            self.stats['negative_membership_tests'] += len(uncovered)
            uncovered = still_uncovered
        self.tick()
        return {'status': 'REJECT' if uncovered else 'ACCEPT'}
