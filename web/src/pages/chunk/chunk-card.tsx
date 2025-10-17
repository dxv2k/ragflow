import Image from '@/components/image';
import { IChunk } from '@/interfaces/database/knowledge';
import { Card, Checkbox, CheckboxProps, Flex, Popover, Switch } from 'antd';
import classNames from 'classnames';
import DOMPurify from 'dompurify';
import { useEffect, useState } from 'react';

import { useTheme } from '@/components/theme-provider';

// Define ChunkTextMode locally to avoid import issues
enum ChunkTextMode {
  Normal = 'normal',
  Ellipse = 'ellipse',
}

// Define styles object to avoid CSS import issues
const styles = {
  chunkCard: 'chunk-card',
  cardSelected: 'card-selected',
  cardSelectedDark: 'card-selected-dark',
  imagePreview: 'image-preview',
  image: 'image',
  content: 'content cursor-pointer',
  contentText: 'content-text',
  contentEllipsis: 'content-ellipsis line-clamp-4',
};

interface IProps {
  item: IChunk;
  checked: boolean;
  switchChunk: (available?: number, chunkIds?: string[]) => void;
  editChunk: (chunkId: string) => void;
  handleCheckboxClick: (chunkId: string, checked: boolean) => void;
  selected: boolean;
  clickChunkCard: (chunkId: string) => void;
  textMode: ChunkTextMode;
}

interface SpeakerSegment {
  speaker: string;
  text: string;
  start?: number;
  end?: number;
}

interface ParsedPageCardProps {
  page: string;
  content: string;
}

// Speaker color classes for different speakers
const speakerColors = [
  'text-blue-600 bg-blue-50 border-blue-200',
  'text-green-600 bg-green-50 border-green-200',
  'text-purple-600 bg-purple-50 border-purple-200',
  'text-orange-600 bg-orange-50 border-orange-200',
  'text-red-600 bg-red-50 border-red-200',
  'text-indigo-600 bg-indigo-50 border-indigo-200',
  'text-yellow-600 bg-yellow-50 border-yellow-200',
  'text-pink-600 bg-pink-50 border-pink-200',
];

function formatTimestamp(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = (seconds % 60).toFixed(1);
  return `${minutes}:${remainingSeconds.padStart(4, '0')}`;
}

function parseSpeakerText(content: string): SpeakerSegment[] {
  console.log(
    '🔍 [Speaker Parser] Input content:',
    content.substring(0, 200) + '...',
  );

  // Remove HTML tags first and get clean text
  const cleanContent = content.replace(/<[^>]*>/g, '').trim();
  console.log(
    '🧹 [Speaker Parser] Clean content (no HTML):',
    cleanContent.substring(0, 200) + '...',
  );

  // Try to parse as JSON first (new WhisperX structure)
  try {
    const jsonData = JSON.parse(cleanContent);

    if (jsonData.segments && Array.isArray(jsonData.segments)) {
      console.log(
        '🎯 [Speaker Parser] Found new WhisperX JSON structure with segments',
      );

      const individualSegments: SpeakerSegment[] = [];

      for (const segment of jsonData.segments) {
        const speaker = segment.speaker || 'UNKNOWN';
        const text = segment.text?.trim() || '';
        const start = segment.start;
        const end = segment.end;

        if (text) {
          // Add each segment individually (no consolidation)
          individualSegments.push({
            speaker: speaker,
            text: text,
            start: start,
            end: end,
          });
          console.log(
            `➕ [Speaker Parser] Added individual ${speaker} segment (${formatTimestamp(start)} - ${formatTimestamp(end)})`,
          );
        }
      }

      console.log(
        `🎯 [Speaker Parser] Total individual segments: ${individualSegments.length}`,
      );
      individualSegments.forEach((seg, idx) => {
        const timeRange =
          seg.start !== undefined && seg.end !== undefined
            ? ` [${formatTimestamp(seg.start)} - ${formatTimestamp(seg.end)}]`
            : '';
        console.log(
          `   ${idx + 1}. ${seg.speaker}${timeRange}: "${seg.text.substring(0, 50)}${seg.text.length > 50 ? '...' : ''}"`,
        );
      });

      return individualSegments;
    }
  } catch (error) {
    console.log(
      '📝 [Speaker Parser] Not JSON or invalid structure, falling back to regex parsing',
    );
  }

  // Fallback to old regex parsing for backward compatibility
  console.log('🔄 [Speaker Parser] Using legacy regex parsing');

  // Match [SPEAKER_XX] pattern followed by text
  const speakerRegex = /\[SPEAKER_(\d+)\]\s*([^[]*?)(?=\[SPEAKER_\d+\]|$)/g;
  const segments: SpeakerSegment[] = [];
  let match;

  while ((match = speakerRegex.exec(cleanContent)) !== null) {
    const speakerNumber = match[1];
    const text = match[2].trim();
    console.log(
      `🎤 [Speaker Parser] Found: SPEAKER_${speakerNumber} -> "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`,
    );

    if (text) {
      segments.push({
        speaker: `SPEAKER_${speakerNumber}`,
        text: text,
      });
    }
  }

  console.log(`📊 [Speaker Parser] Total segments found: ${segments.length}`);
  segments.forEach((seg, idx) => {
    console.log(
      `   ${idx + 1}. ${seg.speaker}: "${seg.text.substring(0, 30)}${seg.text.length > 30 ? '...' : ''}"`,
    );
  });

  return segments;
}

function renderContent(item: IChunk, textMode: ChunkTextMode) {
  console.log('🎨 [Render Content] Starting render for chunk:', item.chunk_id);
  console.log('🎨 [Render Content] Text mode:', textMode);
  console.log(
    '🎨 [Render Content] Raw content:',
    item.content_with_weight.substring(0, 150) + '...',
  );

  const segments = parseSpeakerText(item.content_with_weight);

  // If no speaker patterns found, render original content
  if (segments.length === 0) {
    console.log(
      '❌ [Render Content] No speaker segments found - rendering original content',
    );
    return (
      <div
        dangerouslySetInnerHTML={{
          __html: DOMPurify.sanitize(item.content_with_weight),
        }}
        className={classNames(styles.contentText, {
          [styles.contentEllipsis]: textMode === ChunkTextMode.Ellipse,
        })}
      />
    );
  }

  console.log(
    `✅ [Render Content] Found ${segments.length} speaker segments - rendering enhanced UI`,
  );

  // Render beautiful speaker segments
  return (
    <div
      className={classNames(styles.contentText, {
        [styles.contentEllipsis]: textMode === ChunkTextMode.Ellipse,
      })}
    >
      <div className="space-y-4">
        {segments.map((segment, index) => {
          const speakerNum = parseInt(segment.speaker.split('_')[1] || '0');
          const colorClass = speakerColors[speakerNum % speakerColors.length];
          const hasTimestamp =
            segment.start !== undefined && segment.end !== undefined;

          console.log(
            `🎨 [Render Content] Rendering segment ${index + 1}: ${segment.speaker} with color ${colorClass}${hasTimestamp ? ` [${formatTimestamp(segment.start!)} - ${formatTimestamp(segment.end!)}]` : ''}`,
          );

          return (
            <div key={index} className="space-y-2">
              {/* Timestamp Header */}
              {hasTimestamp && (
                <div className="text-sm font-semibold text-gray-700 bg-gray-100 px-3 py-2 rounded-md border">
                  Timestamp {index + 1}: {formatTimestamp(segment.start!)} -{' '}
                  {formatTimestamp(segment.end!)}
                </div>
              )}

              {/* Speaker and Text with indentation */}
              <div className="ml-4 space-y-2">
                <div className="flex items-center gap-2">
                  <div
                    className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${colorClass}`}
                  >
                    🎤 {segment.speaker.replace('SPEAKER_', 'Speaker ')}
                  </div>
                </div>
                <div className="text-gray-800 text-sm leading-relaxed pl-3 border-l-3 border-gray-300 bg-gray-50 p-3 rounded-r-md">
                  {segment.text}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Export ChunkCard as named export (required by other files)
export const ChunkCard = ({
  item,
  checked,
  handleCheckboxClick,
  editChunk,
  switchChunk,
  selected,
  clickChunkCard,
  textMode,
}: IProps) => {
  console.log('🧩 [ChunkCard] Rendering chunk card for:', item.chunk_id);
  console.log(
    '🧩 [ChunkCard] Content preview:',
    item.content_with_weight.substring(0, 100) + '...',
  );
  console.log(
    '🧩 [ChunkCard] Text mode:',
    textMode,
    'Selected:',
    selected,
    'Checked:',
    checked,
  );

  const available = Number(item.available_int);
  const [enabled, setEnabled] = useState(false);
  const { theme } = useTheme();

  const onChange = (checked: boolean) => {
    setEnabled(checked);
    switchChunk(available === 0 ? 1 : 0, [item.chunk_id]);
  };

  const handleCheck: CheckboxProps['onChange'] = (e) => {
    handleCheckboxClick(item.chunk_id, e.target.checked);
  };

  const handleContentDoubleClick = () => {
    console.log(
      '🖱️ [ChunkCard] Double-clicked chunk for editing:',
      item.chunk_id,
    );
    editChunk(item.chunk_id);
  };

  const handleContentClick = () => {
    console.log('🖱️ [ChunkCard] Clicked chunk:', item.chunk_id);
    clickChunkCard(item.chunk_id);
  };

  useEffect(() => {
    setEnabled(available === 1);
  }, [available]);

  console.log(
    '🧩 [ChunkCard] About to render content section for chunk:',
    item.chunk_id,
  );

  return (
    <Card
      className={classNames(styles.chunkCard, {
        [`${theme === 'dark' ? styles.cardSelectedDark : styles.cardSelected}`]:
          selected,
      })}
    >
      <Flex gap={'middle'} justify={'space-between'}>
        <Checkbox onChange={handleCheck} checked={checked}></Checkbox>
        {item.image_id && (
          <Popover
            placement="right"
            content={
              <Image id={item.image_id} className={styles.imagePreview}></Image>
            }
          >
            <Image id={item.image_id} className={styles.image}></Image>
          </Popover>
        )}

        <section
          onDoubleClick={handleContentDoubleClick}
          onClick={handleContentClick}
          className={styles.content}
        >
          {renderContent(item, textMode)}
        </section>

        <div>
          <Switch checked={enabled} onChange={onChange} />
        </div>
      </Flex>
    </Card>
  );
};

// Export ParsedPageCard as named export (required by other files)
export function ParsedPageCard({ page, content }: ParsedPageCardProps) {
  console.log('📄 [ParsedPageCard] Rendering page card for:', page);
  console.log(
    '📄 [ParsedPageCard] Content preview:',
    content.substring(0, 100) + '...',
  );

  const segments = parseSpeakerText(content);

  // If no speaker patterns found, render simple card
  if (segments.length === 0) {
    console.log(
      '❌ [ParsedPageCard] No speaker segments - rendering simple card',
    );
    return (
      <Card className="bg-gray-50 border-gray-200 rounded-xl mb-4">
        <div className="p-4">
          <p className="text-gray-600 text-sm mb-2">{page}</p>
          <div className="text-gray-800 text-base">{content}</div>
        </div>
      </Card>
    );
  }

  console.log(
    `✅ [ParsedPageCard] Found ${segments.length} speaker segments - rendering enhanced card`,
  );

  // Render with speaker segments
  return (
    <Card className="bg-gray-50 border-gray-200 rounded-xl mb-4">
      <div className="p-4">
        <p className="text-gray-600 text-sm mb-3">{page}</p>
        <div className="space-y-4">
          {segments.map((segment, index) => {
            const speakerNum = parseInt(segment.speaker.split('_')[1] || '0');
            const colorClass = speakerColors[speakerNum % speakerColors.length];
            const hasTimestamp =
              segment.start !== undefined && segment.end !== undefined;

            console.log(
              `📄 [ParsedPageCard] Rendering segment ${index + 1} for page ${page}: ${segment.speaker}${hasTimestamp ? ` [${formatTimestamp(segment.start!)} - ${formatTimestamp(segment.end!)}]` : ''}`,
            );

            return (
              <div key={index} className="space-y-2">
                {/* Timestamp Header */}
                {hasTimestamp && (
                  <div className="text-sm font-semibold text-gray-700 bg-gray-100 px-3 py-2 rounded-md border">
                    📅 Timestamp{index}: {formatTimestamp(segment.start!)} -{' '}
                    {formatTimestamp(segment.end!)}
                  </div>
                )}

                {/* Speaker and Text with indentation */}
                <div className="ml-4 space-y-2">
                  <div className="flex items-center gap-2">
                    <div
                      className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${colorClass}`}
                    >
                      🎤 {segment.speaker.replace('SPEAKER_', 'Speaker ')}
                    </div>
                  </div>
                  <div className="text-gray-800 text-sm leading-relaxed pl-3 border-l-3 border-gray-300 bg-white p-2 rounded-r-md">
                    {segment.text}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}

// Default export for compatibility
export default ChunkCard;
