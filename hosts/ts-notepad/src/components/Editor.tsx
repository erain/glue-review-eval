/** Plain-textarea markdown editor. */

export interface EditorProps {
  value: string;
  onChange: (next: string) => void;
  disabled?: boolean;
}

export default function Editor({ value, onChange, disabled }: EditorProps) {
  return (
    <textarea
      className="editor"
      aria-label="Note editor"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      spellCheck
      placeholder={disabled ? '' : 'Write some markdown...'}
    />
  );
}
